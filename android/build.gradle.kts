name: Build APK
on:
  workflow_dispatch:
  push:
    paths:
      - "android/**"
      - ".github/workflows/build-apk.yml"
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"
      - name: Build debug APK
        working-directory: android
        run: gradle assembleDebug --no-daemon
      - name: Publish APK to the latest release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          cp android/app/build/outputs/apk/debug/app-debug.apk sejal-ai.apk
          gh release delete latest --cleanup-tag --yes || true
          gh release create latest sejal-ai.apk --title "Latest APK" --notes "Auto-built debug APK" --prerelease
