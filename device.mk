#
# Copyright (C) 2025 The Android Open Source Project
# Copyright (C) 2025 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/samsung/gta4lve

PRODUCT_PACKAGES += \
    fastbootd \
    android.hardware.fastboot@1.0-service \
    android.hardware.fastboot@1.1-service \
    android.hardware.fastboot@1.0-impl \
    android.hardware.fastboot@1.0-impl-mock \
    android.hardware.fastboot@1.1-impl-mock \
    android.hardware.boot@1.0-service \
    android.hardware.boot@1.1-service \
    android.hardware.boot@1.0-impl \
    bootctrl.$(PRODUCT_PLATFORM) \
    bootctrl.$(PRODUCT_PLATFORM).recovery \
    android.hardware.health@2.1-service \
    hwservicemanager \
    vndservicemanager

# Crypto and Security (Required for FBE Decryption)
PRODUCT_PACKAGES += \
    android.hardware.gatekeeper@1.0-service \
    android.hardware.gatekeeper@1.0-impl \
    android.hardware.keymaster@4.0-service \
    android.hardware.keymaster@4.0-impl \
    android.hardware.confirmationui@1.0-service \
    android.hardware.confirmationui@1.0-impl

# Graphics and Display (Specific for Unisoc/Spreadtrum platform stability)
PRODUCT_PACKAGES += \
    android.hardware.graphics.composer@2.1-impl \
    android.hardware.graphics.composer@2.1-service \
    android.hardware.graphics.mapper@2.0-impl-2.1 \
    android.hardware.graphics.common@1.1

# USB and Connectivity
PRODUCT_PACKAGES += \
    android.hardware.usb@1.0-service \
    android.hardware.usb@1.0-impl

# Dynamic partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true
PRODUCT_SHIPPING_API_LEVEL := 30
TARGET_OTA_ASSERT_DEVICE := gta4lve
