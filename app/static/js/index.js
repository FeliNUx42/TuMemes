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


/*
// grow textarea for creating / editing Post

function autoGrow(element) {
  window.setTimeout(() => {
    element.style.height = "auto";
    element.style.height = element.scrollHeight + "px";
  }, 0);
}

// Read more

function readMoreFunc() {
  const readMore = document.querySelectorAll(".read-more");
  readMore.forEach(elem => {
    if (elem.offsetHeight < 100)  return;
    
    elem.classList.add("hide-overflow");
    let btn = document.createElement("div");
    btn.classList.add("read-more-div");
    btn.appendChild(document.createElement("a"));
    elem.parentElement.appendChild(btn);
  })

  const readMoreBtn = document.querySelectorAll(".read-more-div a");
  readMoreBtn.forEach(elem => {
    elem.addEventListener("click", () => {
      elem.parentNode.parentNode.classList.toggle("read-more-active")
    });
  })
}

readMoreFunc();

// change mode: edit - preview
function changeMode(element, body) {
  if (element.classList.contains("tab-active")) return;
  
  const buttons = document.querySelectorAll(".tab-bar button");
  const windows = document.querySelectorAll(".tab-window")

  buttons.forEach(button => {
    if (button.classList.contains("tab-active")) button.classList.remove("tab-active");
  });

  element.classList.add("tab-active")

  windows.forEach(window => {
    if (window.classList.contains("tab-active")) window.classList.remove("tab-active")
    if (window.classList.contains(body)) window.classList.add("tab-active")
  })

  readMoreFunc();
  
  if (body == "tab-preview") {
    let preview = document.querySelector(".tab-preview")
    let req = new XMLHttpRequest();
    let url = "/markdown";
    let param = "data=" + document.querySelector("#data").value.replaceAll("&", "%26");

    req.onreadystatechange = () => {
      if (req.readyState == 4 && req.status == 200) {
        let title = document.querySelector("#title").value;
        let description = document.querySelector("#description").value;
        let banner = `<div class="post-banner"><div class="post-banner-top"><h1>${title}</h1></div><hr><p class "post-banner-description">${description}</p></div>`
        preview.innerHTML = banner + '<div class="markdown-body">' + req.responseText + '</div>';
      }
    }

    req.open("POST", url, true)
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    req.send(param);
  }
}
*/

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