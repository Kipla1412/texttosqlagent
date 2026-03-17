const contacts = [
  {
    id: 1,
    name: "Alice",
    avatar: "A",
    messages: [
      { from: "them", text: "Hey! How are you?" },
      { from: "me", text: "I'm good, thanks! And you?" },
      { from: "them", text: "Doing well :)" },
    ],
  },
  {
    id: 2,
    name: "Bob",
    avatar: "B",
    messages: [
      { from: "me", text: "Hi Bob!" },
      { from: "them", text: "Hello!" },
    ],
  },
  {
    id: 3,
    name: "Charlie",
    avatar: "C",
    messages: [
      { from: "them", text: "This is the start of our chat." },
    ],
  },
];

let currentContact = null;

function renderContacts() {
  const contactsList = document.getElementById("contactsList");
  contactsList.innerHTML = "";
  contacts.forEach((contact, idx) => {
    const li = document.createElement("li");
    li.className = "contact-item" + (currentContact && contact.id === currentContact.id ? " selected" : "");
    li.dataset.id = contact.id;

    li.innerHTML = `
      <span class="contact-avatar">${contact.avatar}</span>
      <span class="contact-info"><span class="contact-name">${contact.name}</span></span>
    `;
    li.onclick = () => {
      selectContact(contact.id);
    };
    contactsList.appendChild(li);
  });
}

function renderChat() {
  const chatHeader = document.getElementById("chatHeader");
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const chatForm = document.getElementById("chatForm");

  if (!currentContact) {
    chatHeader.querySelector(".contact-name").innerText = "Select a chat";
    chatMessages.innerHTML = '<div class="placeholder">Select a contact to start chatting</div>';
    chatInput.disabled = true;
    chatForm.querySelector("button").disabled = true;
    return;
  }

  chatHeader.querySelector(".contact-name").innerText = currentContact.name;
  chatMessages.innerHTML = "";
  currentContact.messages.forEach(msg => {
    const div = document.createElement("div");
    div.className = "message " + (msg.from === "me" ? "sent" : "received");
    div.innerText = msg.text;
    chatMessages.appendChild(div);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
  chatInput.disabled = false;
  chatForm.querySelector("button").disabled = false;
}

function selectContact(id) {
  currentContact = contacts.find(c => c.id === id);
  renderContacts();
  renderChat();
}

document.getElementById("chatForm").addEventListener("submit", function(e) {
  e.preventDefault();
  if (!currentContact) return;
  const input = document.getElementById("chatInput");
  const text = input.value.trim();
  if (!text) return;
  currentContact.messages.push({ from: "me", text });
  renderChat();
  input.value = "";
});

// Initial render
renderContacts();
renderChat();
