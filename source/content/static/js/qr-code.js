// QR Code functionality for StoneWalker
class QRCodeManager {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.scanning = false;
        this.html5QrScanner = null;
    }

    // Generate QR code using server API
    async generateQRCode(stoneName, stoneUUID) {
        try {
            const response = await fetch(`/api/generate-qr/?stone_name=${encodeURIComponent(stoneName)}&stone_uuid=${stoneUUID}`);
            const data = await response.json();
            
            if (data.success) {
                return {
                    qrCode: data.qr_code,
                    qrUrl: data.qr_url,
                    stoneName: data.stone_name,
                    stoneUUID: data.stone_uuid
                };
            } else {
                throw new Error(data.error || 'Failed to generate QR code');
            }
        } catch (error) {
            console.error('Error generating QR code:', error);
            throw error;
        }
    }

    // Display QR code in container
    displayQRCode(containerId, qrCodeData) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Create QR code image
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${qrCodeData.qrCode}`;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';

        // Clear container and add image
        container.innerHTML = '';
        container.appendChild(img);

        // Add cleartext URL underneath QR code
        const cleartextDiv = document.createElement('div');
        cleartextDiv.style.marginTop = '8px';
        cleartextDiv.style.textAlign = 'center';
        cleartextDiv.innerHTML = `
            <p style="margin: 0; color: #666; font-size: 10px; word-break: break-all; line-height: 1.2; background: #f8f8f8; padding: 4px 6px; border-radius: 3px; border: 1px solid #e0e0e0;">
                ${qrCodeData.qrUrl}
            </p>
        `;
        container.appendChild(cleartextDiv);

        // Update info display
        this.updateQRInfo(qrCodeData);
    }

    // Update QR code information display
    updateQRInfo(qrCodeData) {
        const infoElements = {
            'qr-stone-name': qrCodeData.stoneName,
            'qr-stone-uuid': qrCodeData.stoneUUID,
            'qr-scan-url': qrCodeData.qrUrl
        };

        Object.entries(infoElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Show info container
        const qrCodeInfo = document.getElementById('qr-code-info');
        if (qrCodeInfo) {
            qrCodeInfo.style.display = 'block';
        }

        // Show download button
        const downloadBtn = document.getElementById('download-qr-btn');
        if (downloadBtn) {
            downloadBtn.style.display = 'inline-block';
        }
    }

    // Download QR code
    downloadQRCode(qrCodeData, filename = null) {
        const link = document.createElement('a');
        link.href = `data:image/png;base64,${qrCodeData.qrCode}`;
        link.download = filename || `${qrCodeData.stoneName}_qr.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Initialize real QR scanner using html5-qrcode
    async initQRScanner(containerId) {
        try {
            const container = document.getElementById(containerId);
            if (!container) return false;

            // Clear container
            container.innerHTML = '<div id="qr-reader"></div>';

            // Check if html5-qrcode library is loaded
            if (typeof Html5QrcodeScanner === 'undefined') {
                // Load the library dynamically
                await this.loadHtml5QrCodeLibrary();
            }

            // Create QR scanner
            this.html5QrScanner = new Html5QrcodeScanner(
                "qr-reader",
                { 
                    fps: 10, 
                    qrbox: 250,
                    aspectRatio: 1.0
                }
            );

            // Render scanner with success callback
            this.html5QrScanner.render(this.onQRCodeDetected.bind(this), this.onQRScanError.bind(this));

            return true;
        } catch (error) {
            console.error('Error initializing QR scanner:', error);
            this.showCameraError(containerId, error.message);
            return false;
        }
    }

    // Load html5-qrcode library dynamically
    async loadHtml5QrCodeLibrary() {
        return new Promise((resolve, reject) => {
            if (typeof Html5QrcodeScanner !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Handle QR code detection
    onQRCodeDetected(decodedText, decodedResult) {
        console.log('QR Code detected:', decodedText);

        // Stop scanning
        this.stopQRScanner();

        // Extract UUID from the decoded text
        // New format: /stone-link/{number}/?key={uuid}
        const newMatch = decodedText.match(/\/stone-link\/(\d+)\/?\?key=([0-9a-f-]+)/i);
        // Legacy: /stone-link/{uuid}/
        const legacyMatch = decodedText.match(/\/stone-link\/([0-9a-f]{8}-[0-9a-f]{4}-)/i);
        if (newMatch) {
            const uuid = newMatch[2];
            this.handleScannedUUID(uuid);
        } else if (legacyMatch) {
            const uuidMatch = decodedText.match(/\/stone-link\/([^\/]+)\//);
            if (uuidMatch) {
                const uuid = uuidMatch[1];
                this.handleScannedUUID(uuid);
            }
        } else {
            // Try to extract UUID directly if it's just a UUID
            const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
            if (uuidRegex.test(decodedText)) {
                this.handleScannedUUID(decodedText);
            } else {
                alert('Invalid QR code format. Please scan a valid StoneWalker QR code.');
            }
        }
    }

    // Handle QR scan errors
    onQRScanError(error) {
        console.log('QR scan error:', error);
        // Don't show error to user for normal scanning process
    }

    // Handle scanned UUID
    handleScannedUUID(uuid) {
        // Update manual input
        const manualInput = document.getElementById('manual-uuid-input');
        if (manualInput) {
            manualInput.value = uuid;
            manualInput.dispatchEvent(new Event('blur'));
        }

        // Show success message
        this.showScanSuccess(uuid);
    }

    // Stop QR scanner
    stopQRScanner() {
        if (this.html5QrScanner) {
            this.html5QrScanner.clear();
            this.html5QrScanner = null;
        }
    }

    // Show camera error
    showCameraError(containerId, errorMessage) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div style="background: #ffebee; border: 2px solid #f44336; border-radius: 8px; padding: 20px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px;">📷</div>
                <p style="color: #d32f2f; margin: 0; font-size: 14px;">Camera Error</p>
                <p style="color: #999; font-size: 11px; margin: 5px 0 0 0;">${errorMessage}</p>
                <p style="color: #666; font-size: 10px; margin: 5px 0 0 0;">Please use manual input instead</p>
            </div>
        `;
    }

    // Show scan success
    showScanSuccess(uuid) {
        const container = document.getElementById('camera-scanner');
        if (!container) return;

        container.innerHTML = `
            <div style="background: #e8f5e8; border: 2px solid #4caf50; border-radius: 8px; padding: 20px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px;">✅</div>
                <p style="color: #2e7d32; margin: 0; font-size: 14px;">QR Code Scanned!</p>
                <p style="color: #666; font-size: 11px; margin: 5px 0 0 0;">UUID: ${uuid}</p>
            </div>
        `;
    }

    // Validate UUID format
    validateUUID(uuid) {
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        return uuidRegex.test(uuid);
    }

    // Check if UUID exists in database
    async checkUUIDExists(uuid) {
        try {
            const response = await fetch(`/api/check-stone-uuid/${uuid}/`);
            const data = await response.json();
            return data.exists;
        } catch (error) {
            console.error('Error checking UUID:', error);
            return false;
        }
    }
}

// Global QR code manager instance
window.qrCodeManager = new QRCodeManager();

// Initialize QR code functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // QR Code generation for new stones
    const downloadQrBtn = document.getElementById('download-qr-btn');
    if (downloadQrBtn) {
        downloadQrBtn.addEventListener('click', async function() {
            const stoneName = document.getElementById('qr-stone-name')?.textContent;
            const stoneUUID = document.getElementById('qr-stone-uuid')?.textContent;
            
            if (stoneName && stoneUUID) {
                try {
                    const qrData = await window.qrCodeManager.generateQRCode(stoneName, stoneUUID);
                    window.qrCodeManager.downloadQRCode(qrData);
                } catch (error) {
                    console.error('Error downloading QR code:', error);
                    alert('Error downloading QR code. Please try again.');
                }
            }
        });
    }

    // Camera initialization for existing code section
    const qrOptionExisting = document.getElementById('qr-option-existing');
    if (qrOptionExisting) {
        qrOptionExisting.addEventListener('click', function() {
            // Initialize QR scanner when existing code option is selected
            setTimeout(() => {
                const cameraScanner = document.getElementById('camera-scanner');
                if (cameraScanner && cameraScanner.style.display !== 'none') {
                    window.qrCodeManager.initQRScanner('camera-scanner');
                }
            }, 100);
        });
    }

    // Manual UUID validation
    const manualUuidInput = document.getElementById('manual-uuid-input');
    if (manualUuidInput) {
        manualUuidInput.addEventListener('blur', async function() {
            const uuid = this.value.trim();
            if (uuid) {
                if (window.qrCodeManager.validateUUID(uuid)) {
                    // Check if UUID exists in database
                    const exists = await window.qrCodeManager.checkUUIDExists(uuid);
                    
                    const validationStatus = document.getElementById('validation-status');
                    const validatedUuid = document.getElementById('validated-uuid');
                    const codeValidation = document.getElementById('code-validation');
                    
                    if (validatedUuid) validatedUuid.textContent = uuid;
                    
                    if (validationStatus) {
                        if (exists) {
                            validationStatus.textContent = 'Valid UUID - Stone found';
                            validationStatus.style.color = '#4CAF50';
                        } else {
                            validationStatus.textContent = 'Valid UUID - Stone not found';
                            validationStatus.style.color = '#FF9800';
                        }
                    }
                    
                    if (codeValidation) codeValidation.style.display = 'block';
                } else {
                    const validationStatus = document.getElementById('validation-status');
                    if (validationStatus) {
                        validationStatus.textContent = 'Invalid UUID format';
                        validationStatus.style.color = '#f44336';
                    }
                }
            }
        });
    }

    // Clean up QR scanner when modals are closed
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                window.qrCodeManager.stopQRScanner();
            });
        }
    });
}); 