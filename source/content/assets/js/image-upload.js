/**
 * Shared image upload validation and auto-resize.
 *
 * Usage:
 *   setupImageUpload({
 *     inputId: 'id_profile_picture',
 *     previewId: 'profile-picture-preview',  // optional <img> for preview
 *     msgId: 'image-validation-msg',          // optional message element
 *     maxDim: 800,                            // max width/height in px
 *     maxSize: 5 * 1024 * 1024,               // max file size in bytes
 *     onValid: function(file, dataUrl) {},     // callback after valid file
 *     onReset: function() {}                   // callback on invalid/reset
 *   });
 */

(function(window) {
  'use strict';

  var DEFAULT_MAX_DIM = 800;
  var DEFAULT_MAX_SIZE = 5 * 1024 * 1024; // 5MB

  /**
   * Format bytes into a human-readable string.
   */
  function formatSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
  }

  /**
   * Determine compression quality based on original file size.
   */
  function getQuality(fileSize) {
    if (fileSize > 2 * 1024 * 1024) return 0.6;
    if (fileSize > 1 * 1024 * 1024) return 0.7;
    return 0.85;
  }

  /**
   * Check if the browser supports WebP encoding via canvas.
   */
  function supportsWebP() {
    try {
      var c = document.createElement('canvas');
      c.width = 1;
      c.height = 1;
      return c.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    } catch (e) {
      return false;
    }
  }

  var useWebP = supportsWebP();

  /**
   * Resize and compress an image file using canvas.
   * Tries WebP first where supported, falls back to JPEG.
   * Returns a Promise that resolves with a File object.
   */
  function resizeImage(file, maxDim) {
    var originalSize = file.size;
    return new Promise(function(resolve) {
      var img = new Image();
      img.onload = function() {
        var w = img.naturalWidth;
        var h = img.naturalHeight;
        var quality = getQuality(originalSize);
        var needsResize = w > maxDim || h > maxDim;
        var needsCompress = originalSize > 1 * 1024 * 1024;

        if (!needsResize && !needsCompress) {
          resolve({ file: file, originalSize: originalSize, compressed: false });
          return;
        }

        if (needsResize) {
          if (w > h) {
            h = Math.round(h * maxDim / w);
            w = maxDim;
          } else {
            w = Math.round(w * maxDim / h);
            h = maxDim;
          }
        }

        var canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);

        var mimeType = useWebP ? 'image/webp' : 'image/jpeg';
        var ext = useWebP ? '.webp' : '.jpg';
        var fileName = file.name.replace(/\.[^.]+$/, '') + ext;

        canvas.toBlob(function(blob) {
          if (!blob) {
            // Fallback to JPEG if WebP blob failed
            mimeType = 'image/jpeg';
            fileName = file.name.replace(/\.[^.]+$/, '') + '.jpg';
            canvas.toBlob(function(jpegBlob) {
              var resizedFile = new File([jpegBlob || file], fileName, {
                type: mimeType,
                lastModified: Date.now()
              });
              resolve({ file: resizedFile, originalSize: originalSize, compressed: true });
            }, 'image/jpeg', quality);
            return;
          }
          var resizedFile = new File([blob], fileName, {
            type: mimeType,
            lastModified: Date.now()
          });
          resolve({ file: resizedFile, originalSize: originalSize, compressed: true });
        }, mimeType, quality);
      };
      img.onerror = function() {
        resolve({ file: file, originalSize: originalSize, compressed: false });
      };
      img.src = URL.createObjectURL(file);
    });
  }

  /**
   * Show a validation message in an element.
   */
  function showMsg(el, text, isError) {
    if (!el) return;
    el.textContent = text;
    el.style.display = text ? 'block' : 'none';
    el.className = 'text-center mb-1 fs-0-95 ' + (isError ? 'text-error' : 'text-success');
  }

  /**
   * Set up image upload validation on a file input.
   */
  function setupImageUpload(opts) {
    var input = document.getElementById(opts.inputId);
    if (!input) return;

    var preview = opts.previewId ? document.getElementById(opts.previewId) : null;
    var msgEl = opts.msgId ? document.getElementById(opts.msgId) : null;
    var maxDim = opts.maxDim || DEFAULT_MAX_DIM;
    var maxSize = opts.maxSize || DEFAULT_MAX_SIZE;
    var onValid = opts.onValid || function() {};
    var onReset = opts.onReset || function() {};

    input.addEventListener('change', function(e) {
      var file = e.target.files[0];
      if (!file) return;

      // Check file type
      if (!file.type.startsWith('image/')) {
        showMsg(msgEl, 'Please select an image file.', true);
        input.value = '';
        onReset();
        return;
      }

      // Check file size
      if (file.size > maxSize) {
        var maxMB = Math.round(maxSize / (1024 * 1024));
        showMsg(msgEl, 'Image is too large (max ' + maxMB + 'MB). Please choose a smaller image.', true);
        input.value = '';
        onReset();
        return;
      }

      // Resize and compress
      resizeImage(file, maxDim).then(function(result) {
        var resizedFile = result.file;

        // Replace file input with processed version
        var dt = new DataTransfer();
        dt.items.add(resizedFile);
        input.files = dt.files;

        // Build feedback message
        var msg = '';
        if (result.compressed) {
          msg = 'Image compressed from ' + formatSize(result.originalSize) + ' to ' + formatSize(resizedFile.size);
          if (useWebP) msg += ' (WebP)';
        }
        showMsg(msgEl, msg, false);

        var reader = new FileReader();
        reader.onload = function(ev) {
          if (preview) preview.src = ev.target.result;
          onValid(resizedFile, ev.target.result);
        };
        reader.readAsDataURL(resizedFile);
      });
    });
  }

  // Expose globally
  window.setupImageUpload = setupImageUpload;
  window.resizeImage = resizeImage;

})(window);
