# Period Manager - Android

APK banane ke 2 tareeqay:

## A) GitHub Actions (sab se asaan, kuch install nahi karna)
1. Is folder ko ek naye GitHub repo mein push karo.
2. Repo -> Actions tab -> "Build APK" workflow khud chalega (ya Run workflow dabao).
3. Khatam hone par Artifacts se **PeriodManager-apk** download karo -> app-debug.apk.

## B) Android Studio
1. Android Studio mein yeh folder open karo, Gradle sync hone do.
2. Build -> Build APK(s). APK: app/build/outputs/apk/debug/app-debug.apk

Phone mein install karte waqt "Install unknown apps" allow karna hoga.
Min Android 10.

Data phone ke andar hi save hota hai (app private storage). PDF -> Downloads folder mein save hoti hai.
