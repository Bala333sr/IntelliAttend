#!/bin/bash

# Script to verify the IntelliAttend Mobile Module structure

echo "Verifying IntelliAttend Mobile Module structure..."

# Check if required directories exist
if [ ! -d "src/main/java/com/intelliattend/mobilemodule" ]; then
    echo "ERROR: Module source directory not found"
    exit 1
fi

if [ ! -d "src/main/res" ]; then
    echo "ERROR: Resources directory not found"
    exit 1
fi

# Check if required files exist
required_files=(
    "build.gradle"
    "README.md"
    "INTEGRATION_GUIDE.md"
    "src/main/AndroidManifest.xml"
    "src/main/java/com/intelliattend/mobilemodule/IntelliAttendMobileModule.kt"
    "src/main/java/com/intelliattend/mobilemodule/collector/BluetoothDataCollector.kt"
    "src/main/java/com/intelliattend/mobilemodule/collector/GPSDataCollector.kt"
    "src/main/java/com/intelliattend/mobilemodule/collector/WiFiDataCollector.kt"
    "src/main/java/com/intelliattend/mobilemodule/collector/EnvironmentalDataCollector.kt"
    "src/main/java/com/intelliattend/mobilemodule/model/EnvironmentalDataModels.kt"
    "src/main/java/com/intelliattend/mobilemodule/repository/EnvironmentalDataRepository.kt"
    "src/main/java/com/intelliattend/mobilemodule/utils/DeviceUtils.kt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: Required file not found: $file"
        exit 1
    fi
done

echo "SUCCESS: All required files and directories are present"
echo "Module structure verified successfully!"