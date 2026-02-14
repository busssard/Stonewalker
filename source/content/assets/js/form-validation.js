/**
 * StoneWalker Form Validation
 * Shared client-side validation for signup and profile edit forms.
 */
var StoneWalkerFormValidation = (function() {

    /**
     * Force lowercase on every keystroke, preserving cursor position.
     */
    function initUsernameLowercase(inputId) {
        var input = document.getElementById(inputId);
        if (!input) return;
        input.addEventListener('input', function() {
            var start = input.selectionStart;
            var end = input.selectionEnd;
            input.value = input.value.toLowerCase();
            input.setSelectionRange(start, end);
        });
    }

    /**
     * Show red "Passwords do not match" when pw2 is non-empty and doesn't match pw1.
     */
    function initPasswordMatch(pw1Id, pw2Id, statusId) {
        var pw1 = document.getElementById(pw1Id);
        var pw2 = document.getElementById(pw2Id);
        var status = document.getElementById(statusId);
        if (!pw1 || !pw2 || !status) return;

        var msgMatch = status.getAttribute('data-match-text') || 'Passwords match';
        var msgNoMatch = status.getAttribute('data-nomatch-text') || 'Passwords do not match';

        function check() {
            var v1 = pw1.value;
            var v2 = pw2.value;
            if (!v2) {
                status.textContent = '';
                status.className = 'pw-match-status';
                return;
            }
            if (v1 === v2) {
                status.textContent = msgMatch;
                status.className = 'pw-match-status pw-match-ok';
            } else {
                status.textContent = msgNoMatch;
                status.className = 'pw-match-status pw-match-fail';
            }
        }

        pw1.addEventListener('input', check);
        pw2.addEventListener('input', check);
    }

    /**
     * Check if password is too similar to personal info.
     * Uses substring matching (case-insensitive) for strings >= 3 chars.
     */
    function isSimilarToPersonalInfo(pw, opts) {
        if (!pw || pw.length < 3) return false;
        var pwLower = pw.toLowerCase();
        var fields = ['usernameId', 'firstNameId', 'lastNameId', 'emailId'];
        for (var i = 0; i < fields.length; i++) {
            var el = opts[fields[i]] ? document.getElementById(opts[fields[i]]) : null;
            var val = el ? el.value.trim().toLowerCase() : '';
            // For email, also check just the local part
            if (fields[i] === 'emailId' && val.indexOf('@') > -1) {
                var localPart = val.split('@')[0];
                if (localPart.length >= 3 && (pwLower.indexOf(localPart) > -1 || localPart.indexOf(pwLower) > -1)) {
                    return true;
                }
            }
            if (val.length >= 3 && (pwLower.indexOf(val) > -1 || val.indexOf(pwLower) > -1)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Show 4 criteria lines that toggle red/green in real-time.
     */
    function initPasswordCriteria(pw1Id, opts) {
        var pw1 = document.getElementById(pw1Id);
        var container = document.getElementById(opts.containerId || 'pw-criteria');
        if (!pw1 || !container) return;

        // Read translated strings from data attributes on container
        var txtLength = container.getAttribute('data-length-text') || 'At least 8 characters';
        var txtNumeric = container.getAttribute('data-numeric-text') || "Can't be entirely numeric";
        var txtCommon = container.getAttribute('data-common-text') || 'Not a commonly used password';
        var txtSimilar = container.getAttribute('data-similar-text') || "Can't be too similar to your personal info";

        // Build criteria elements
        var criteria = [
            { el: null, text: txtLength },
            { el: null, text: txtNumeric },
            { el: null, text: txtCommon },
            { el: null, text: txtSimilar }
        ];

        container.innerHTML = '';
        for (var i = 0; i < criteria.length; i++) {
            var div = document.createElement('div');
            div.className = 'pw-criterion';
            div.textContent = criteria[i].text;
            container.appendChild(div);
            criteria[i].el = div;
        }

        function check() {
            var pw = pw1.value;
            if (!pw) {
                for (var i = 0; i < criteria.length; i++) {
                    criteria[i].el.className = 'pw-criterion';
                }
                return;
            }

            // 1. At least 8 characters
            criteria[0].el.className = pw.length >= 8 ? 'pw-criterion pw-criterion-pass' : 'pw-criterion pw-criterion-fail';

            // 2. Can't be entirely numeric
            criteria[1].el.className = !/^\d+$/.test(pw) ? 'pw-criterion pw-criterion-pass' : 'pw-criterion pw-criterion-fail';

            // 3. Not a commonly used password
            var isCommon = (typeof COMMON_PASSWORDS !== 'undefined') && COMMON_PASSWORDS.has(pw.toLowerCase());
            criteria[2].el.className = !isCommon ? 'pw-criterion pw-criterion-pass' : 'pw-criterion pw-criterion-fail';

            // 4. Can't be too similar to personal info
            var isSimilar = isSimilarToPersonalInfo(pw, opts);
            criteria[3].el.className = !isSimilar ? 'pw-criterion pw-criterion-pass' : 'pw-criterion pw-criterion-fail';
        }

        pw1.addEventListener('input', check);
        // Also re-check when personal info fields change
        var infoFields = ['usernameId', 'firstNameId', 'lastNameId', 'emailId'];
        for (var j = 0; j < infoFields.length; j++) {
            var el = opts[infoFields[j]] ? document.getElementById(opts[infoFields[j]]) : null;
            if (el) {
                el.addEventListener('input', check);
            }
        }
    }

    /**
     * Debounced API call to check username availability.
     */
    function initUsernameAvailability(inputId, statusId, opts) {
        var input = document.getElementById(inputId);
        var status = document.getElementById(statusId);
        if (!input || !status) return;

        var checkmarkId = opts.checkmarkId;
        var checkmark = checkmarkId ? document.getElementById(checkmarkId) : null;
        var currentUsername = (opts.currentUsername || '').toLowerCase();
        var timeout = null;

        var txtAvailable = status.getAttribute('data-available-text') || 'This username is available!';
        var txtTaken = status.getAttribute('data-taken-text') || 'This username is already taken.';
        var txtEmpty = status.getAttribute('data-empty-text') || 'Username cannot be empty.';
        var txtWhitespace = status.getAttribute('data-whitespace-text') || 'No spaces allowed.';
        var txtCurrent = status.getAttribute('data-current-text') || 'You can change your username';

        function setResult(text, cls) {
            status.textContent = text;
            status.className = 'js-result-text ' + cls;
            if (checkmark) {
                if (cls === 'js-result-valid') {
                    checkmark.className = 'js-checkmark js-checkmark-valid';
                } else if (cls === 'js-result-invalid') {
                    checkmark.className = 'js-checkmark js-checkmark-invalid';
                } else {
                    checkmark.className = 'js-checkmark js-checkmark-neutral';
                }
                checkmark.textContent = '';
            }
        }

        function doCheck() {
            var username = input.value.trim().toLowerCase();
            if (!username) {
                setResult(txtEmpty, 'js-result-neutral');
                return;
            }
            if (currentUsername && username === currentUsername) {
                setResult(txtCurrent, 'js-result-neutral');
                return;
            }
            fetch('/accounts/api/check_username/?username=' + encodeURIComponent(username))
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.taken) {
                        if (data.reason === 'whitespace') {
                            setResult(txtWhitespace, 'js-result-invalid');
                        } else if (data.reason === 'taken') {
                            setResult(txtTaken, 'js-result-invalid');
                        } else if (data.reason === 'empty') {
                            setResult(txtEmpty, 'js-result-neutral');
                        } else {
                            setResult(txtTaken, 'js-result-invalid');
                        }
                    } else {
                        setResult(txtAvailable, 'js-result-valid');
                    }
                });
        }

        input.addEventListener('input', function() {
            if (checkmark) {
                checkmark.textContent = '';
                checkmark.className = 'js-checkmark js-checkmark-neutral';
            }
            status.textContent = '';
            status.className = 'js-result-text js-result-neutral';
            if (timeout) clearTimeout(timeout);
            timeout = setTimeout(doCheck, 350);
        });

        // Initial check on page load
        doCheck();
    }

    return {
        initUsernameLowercase: initUsernameLowercase,
        initPasswordMatch: initPasswordMatch,
        initPasswordCriteria: initPasswordCriteria,
        initUsernameAvailability: initUsernameAvailability
    };
})();
