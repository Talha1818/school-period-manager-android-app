package com.ghsjalhan.periodmanager;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.AssetManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.KeyEvent;
import android.webkit.URLUtil;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {

    private static final int PORT = 8000;
    private static final String BASE_URL = "http://127.0.0.1:" + PORT + "/";
    private static final int VERSION = 1; // bump when the bundled project changes

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        setContentView(webView);
        setupWebView();
        webView.loadData(
                "<html><body style='font-family:sans-serif;text-align:center;padding-top:40vh;color:#1E3A8A'>"
                        + "<h3>Period Manager</h3><p>Loading...</p></body></html>",
                "text/html", "utf-8");

        new Thread(this::bootServer).start();
    }

    private void setupWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setBuiltInZoomControls(false);
        s.setUseWideViewPort(true);      // honour <meta viewport width=device-width>
        s.setLoadWithOverviewMode(false); // don't shrink the page to fit
        s.setTextZoom(100);               // ignore system font scaling breaking the layout

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (url.startsWith(BASE_URL)) return false;
                startActivity(new Intent(Intent.ACTION_VIEW, request.getUrl()));
                return true;
            }
        });

        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) ->
                downloadFile(url, contentDisposition, mimeType));
    }

    private void bootServer() {
        try {
            File projectDir = new File(getFilesDir(), "project");
            File dataDir = new File(getFilesDir(), "data");
            SharedPreferences prefs = getSharedPreferences("pm", MODE_PRIVATE);

            // (Re)extract the bundled Django project on first run / app update.
            // The database lives in data/, so it is never touched here.
            if (!projectDir.exists() || prefs.getInt("extracted_version", 0) != VERSION) {
                deleteRecursive(projectDir);
                copyAsset(getAssets(), "project", projectDir);
                prefs.edit().putInt("extracted_version", VERSION).apply();
            }

            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(this));
            }
            Python.getInstance().getModule("server")
                    .callAttr("start", projectDir.getAbsolutePath(), dataDir.getAbsolutePath(), PORT);

            runOnUiThread(() -> webView.loadUrl(BASE_URL));
        } catch (final Throwable t) {
            runOnUiThread(() -> webView.loadData(
                    "<html><body style='font-family:sans-serif;padding:24px'><h3>Startup error</h3><pre>"
                            + t.toString().replace("<", "&lt;") + "</pre></body></html>",
                    "text/html", "utf-8"));
        }
    }

    private void downloadFile(final String url, final String contentDisposition, final String mimeType) {
        new Thread(() -> {
            try {
                HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
                String name = URLUtil.guessFileName(url, contentDisposition, mimeType);
                String type = mimeType != null && !mimeType.isEmpty() ? mimeType : "application/octet-stream";

                ContentValues cv = new ContentValues();
                cv.put(MediaStore.Downloads.DISPLAY_NAME, name);
                cv.put(MediaStore.Downloads.MIME_TYPE, type);
                cv.put(MediaStore.Downloads.IS_PENDING, 1);
                Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (uri == null) throw new Exception("Could not create file in Downloads");

                try (InputStream in = conn.getInputStream();
                     OutputStream out = getContentResolver().openOutputStream(uri)) {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
                }
                cv.clear();
                cv.put(MediaStore.Downloads.IS_PENDING, 0);
                getContentResolver().update(uri, cv, null, null);

                final Uri saved = uri;
                final String finalType = type;
                final String finalName = name;
                runOnUiThread(() -> {
                    Toast.makeText(this, "Saved to Downloads: " + finalName, Toast.LENGTH_LONG).show();
                    try {
                        Intent view = new Intent(Intent.ACTION_VIEW);
                        view.setDataAndType(saved, finalType);
                        view.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivity(view);
                    } catch (Exception ignored) {
                        // no viewer installed; file is still in Downloads
                    }
                });
            } catch (final Exception e) {
                runOnUiThread(() ->
                        Toast.makeText(this, "Download failed: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        }).start();
    }

    private static void copyAsset(AssetManager am, String assetPath, File dest) throws Exception {
        String[] children = am.list(assetPath);
        if (children != null && children.length > 0) {
            dest.mkdirs();
            for (String child : children) {
                copyAsset(am, assetPath + "/" + child, new File(dest, child));
            }
        } else {
            File parent = dest.getParentFile();
            if (parent != null) parent.mkdirs();
            try (InputStream in = am.open(assetPath);
                 FileOutputStream out = new FileOutputStream(dest)) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            }
        }
    }

    private static void deleteRecursive(File f) {
        if (f.isDirectory()) {
            File[] kids = f.listFiles();
            if (kids != null) for (File k : kids) deleteRecursive(k);
        }
        f.delete();
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
