function displayError(errorMessage) {
    var errorContainer = document.getElementById('error-container');

    // Clear existing error messages
    errorContainer.innerHTML = '';

    // Display new error message
    var errorElement = document.createElement('div');
    errorElement.className = 'text-sm text-center text-pink-600 mt-1';
    errorElement.innerHTML = errorMessage;

    // Apply fixed width and allow text to break
    errorElement.style.maxWidth = '200px';  // Set your desired fixed width
    errorElement.style.wordWrap = 'break-word';  // Allow text to break
    errorElement.style.margin = '0 auto'; // Center the text

    errorContainer.appendChild(errorElement);
  }

  function validateEmail() {
    var email = document.getElementById('email').value;
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      displayError('Invalid email address');
      return false;
    }
    return true;
  }

  function validateUsername() {
    var username = document.getElementById('username').value;
    if (username.length < 6) {
      displayError('Username must be at least 6 characters long');
      return false;
    }
    return true;
  }

  function validatePassword() {
    var password = document.getElementById('password').value;
    var passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*]).{8,}$/;
    if (!passwordRegex.test(password)) {
      displayError('Password must be at least 8 characters with at least 1 uppercase letter, 1 lowercase letter, and 1 symbol');
      return false;
    }
    return true;
  }

  function validatePasswordMatch() {
    var password = document.getElementById('password').value;
    var verifyPassword = document.getElementById('verifyPassword').value;
    if (password !== verifyPassword) {
      displayError('Passwords do not match');
      return false;
    }
    return true;
  }

  function validateForm() {
    clearErrors(); // Clear existing error messages
    var isPasswordMatchValid = validatePasswordMatch();
    var isPasswordValid = validatePassword();
    var isUsernameValid = validateUsername();
    var isEmailValid = validateEmail();

    if (isEmailValid && isUsernameValid && isPasswordValid && isPasswordMatchValid) {
        // Only check username availability if other validations pass
        checkUsernameAvailability();
    }

    // Always return false to prevent the default form submission
    return false;
}

function checkUsernameAvailability() {
    var username = document.getElementById('username').value;

    fetch('/auth/check_username_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=' + username,
    })
    .then(response => response.json())
    .then(data => {
        var errorContainer = document.getElementById('error-container');
        if (data.exists) {
            errorContainer.textContent = 'Username already exists. Please choose a different one.';
        } else {
            // Clear the error message if the username is available
            errorContainer.textContent = '';
            // If everything is valid, you can submit the form programmatically
            document.querySelector('form').submit();
        }
    })
    .catch(error => console.error('Error:', error));
}

function clearErrors() {
    // Add code to clear any existing error messages
    var errorContainer = document.getElementById('error-container');
    errorContainer.textContent = '';
}

