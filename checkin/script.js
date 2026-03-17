function checkName() {
  const input = document.getElementById('nameInput');
  const message = document.getElementById('nameMessage');
  let name = input.value.trim();

  if (!name) {
    message.textContent = 'Please enter your name.';
    message.style.color = '#e63b1c';
    return;
  }
  // Simple validation: name should be at least 2 characters
  if (name.length < 2) {
    message.textContent = 'Name must be at least 2 characters.';
    message.style.color = '#e63b1c';
    return;
  }
  message.textContent = `Welcome, ${name}!`;
  message.style.color = '#1576e6';
}