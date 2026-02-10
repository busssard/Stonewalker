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
   * Resize an image file to max dimensions using canvas.
   * Returns a Promise that resolves with a File object.
   */
  function resizeImage(file, maxDim) {
    return new Promise(function(resolve) {
      var img = new Image();
      img.onload = function() {
        var w = img.naturalWidth;
        var h = img.naturalHeight;
        if (w <= maxDim && h <= maxDim) {
          resolve(file);
          return;
        }
        if (w > h) {
          h = Math.round(h * maxDim / w);
          w = maxDim;
        } else {
          w = Math.round(w * maxDim / h);
          h = maxDim;
        }
        var canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        canvas.toBlob(function(blob) {
          var resizedFile = new File([blob], file.name, {
            type: 'image/jpeg',
            lastModified: Date.now()
          });
          resolve(resizedFile);
        }, 'image/jpeg', 0.85);
      };
      img.onerror = function() {
        resolve(file);
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

      // Check dimensions and resize if needed
      var img = new Image();
      img.onload = function() {
        var w = img.naturalWidth;
        var h = img.naturalHeight;

        if (w > maxDim || h > maxDim) {
          showMsg(msgEl, 'Image resized to fit ' + maxDim + 'x' + maxDim + 'px.', false);
          resizeImage(file, maxDim).then(function(resizedFile) {
            // Replace file input with resized version
            var dt = new DataTransfer();
            dt.items.add(resizedFile);
            input.files = dt.files;

            var reader = new FileReader();
            reader.onload = function(ev) {
              if (preview) preview.src = ev.target.result;
              onValid(resizedFile, ev.target.result);
            };
            reader.readAsDataURL(resizedFile);
          });
        } else {
          showMsg(msgEl, '', false);
          var reader = new FileReader();
          reader.onload = function(ev) {
            if (preview) preview.src = ev.target.result;
            onValid(file, ev.target.result);
          };
          reader.readAsDataURL(file);
        }
      };
      img.onerror = function() {
        showMsg(msgEl, 'Could not read the image. Please try a different file.', true);
        input.value = '';
        onReset();
      };
      img.src = URL.createObjectURL(file);
    });
  }

  // Expose globally
  window.setupImageUpload = setupImageUpload;
  window.resizeImage = resizeImage;

})(window);
