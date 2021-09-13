// collapse navbar

const nav = document.querySelector(".nav-collapse");
const btn = document.querySelector(".nav-collapse-button");

btn.addEventListener("click", () => {
  nav.classList.toggle("nav-active");
});


// close alerts

function alertClose (element) {
  element.parentNode.classList.add("alert-hidden");
}


// expand search area
function expandSearch() {
  document.querySelector("main .search form").classList.toggle("expand");
}

// make a match
const hearts = document.querySelectorAll(".match")
hearts.forEach(heart => {
  heart.addEventListener("click", () => {
    heart.classList.toggle("fas");
    heart.classList.toggle("far");

    let req = new XMLHttpRequest();
    let url = heart.attributes.url.value;
    let param = heart.attributes.param.value;

    req.open("POST", url, true)
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    req.send(param);
  });
})

// hide / show chats
const contacts = document.querySelectorAll(".msg-sender");
const chats = document.querySelectorAll(".msg-chat");

contacts.forEach(contact => {
  contact.addEventListener("click", () => {
    if (contact.classList.contains("current-sender")) return

    contacts.forEach(c => {
      if (c.classList.contains("current-sender")) c.classList.remove("current-sender")
    });

    chats.forEach(c => {
      if (c.classList.contains("current-chat")) c.classList.remove("current-chat")
    });

    contact.classList.add("current-sender")
    document.getElementById(contact.attributes.target.value).classList.add("current-chat")
  });
});


// grow textarea for creating / editing Post

function autoGrow(event) {
  window.setTimeout(() => {
    this.style.height = "40px";
    if (this.scrollHeight > 200) {
      this.style.height = "200px";
      this.style.overflowY = "auto"
      return;
    }
    this.style.height = this.scrollHeight + "px";
  }, 0);
}

// submit form if enter, not if shift enter

function checkSubmit(event) {
  if (event.keyCode == 13 && !event.shiftKey) {
    event.preventDefault()
    event.stopPropagation()
    this.parentNode.submit()
  }
}

const textarea = document.querySelector("textarea");
textarea.addEventListener('keydown', autoGrow);
textarea.addEventListener('keydown', checkSubmit)

if (textarea) {
  autoGrow.call(textarea)
}

// allow new line

const msgContent = document.querySelectorAll(".msg-content .msg-body");
msgContent.forEach(msg => {
  msg.innerHTML = msg.innerHTML.replaceAll("&lt;br&gt;", "<br>");
});

// scroll to bottom

const msgContainers = document.querySelectorAll(".msg-container")

function scrollBottom(element) {
  window.setTimeout(() => {
    element.scrollTo({top: element.scrollHeight});
  }, 0);
}

msgContainers.forEach(container => scrollBottom(container))

// (de)activate passwords in settings

const checkbox = document.querySelector("#activate-pwd");
const pwd = document.querySelector(".settings-passwords");

checkbox.addEventListener("change", e => {
  pwd.classList.toggle("pwd-hidden");
  document.querySelectorAll(".settings-passwords input").forEach( element => {
    element.value = e.target.checked ? "" : "none";
  });
});

// preview meme

const inpMemes = document.querySelectorAll("main form .input-meme");

inpMemes.forEach(inpMeme => {
  inpMeme.addEventListener("change", function () {
    const file = this.files[0];
    const preview = document.getElementById(inpMeme.attributes.target.nodeValue);
    console.log(preview);

    if (file) {
      const reader = new FileReader();

      reader.addEventListener("load", function () {
        preview.setAttribute("src", this.result);
      });

      reader.readAsDataURL(file);
    }
  });
});