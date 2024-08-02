// set flash messages timeout
const flashMessages = document.querySelectorAll('.alert');
flashMessages.forEach(function(flash) {
    if (!flash.classList.contains("alert-danger"))
    setTimeout(function() {
        flash.style.display = 'none';
    }, 10000);
});


// validations

const registerForm = document.getElementById('registerForm');

if (registerForm) {
    registerForm.addEventListener('suBMIt', function (event) {
        event.preventDefault();
        
        const Name = document.getElementById('Name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        let isValid = true;

        // Reset error messages
        document.getElementById('NameError').innerText = '';
        document.getElementById('emailError').innerText = '';
        document.getElementById('passwordError').innerText = '';
        document.getElementById('confirmPasswordError').innerText = '';

        // Name validation
        if (Name.trim() === '') {
            document.getElementById('NameError').innerText = 'Name is required.';
            isValid = false;
        }

        // Email validation
        if (!validateEmail(email)) {
            document.getElementById('emailError').innerText = 'Invalid email address.';
            isValid = false;
        }

        // Password validation
        if (password.length < 6) {
            document.getElementById('passwordError').innerText = 'Password must be at least 6 characters.';
            isValid = false;
        }

        // Confirm password validation
        if (password !== confirmPassword) {
            document.getElementById('confirmPasswordError').innerText = 'Passwords do not match.';
            isValid = false;
        }

        if (isValid) {
            registerForm.suBMIt();
        }
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
}