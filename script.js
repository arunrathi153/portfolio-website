// script.js

// Scroll-triggered fade-in animation
const faders = document.querySelectorAll('.fade-in');

const appearOptions = {
  threshold: 0.2,
  rootMargin: "0px 0px -50px 0px"
};

const appearOnScroll = new IntersectionObserver(function(
  entries,
  appearOnScroll
) {
  entries.forEach(entry => {
    if (!entry.isIntersecting) {
      return;
    } else {
      entry.target.classList.add("appear");
      appearOnScroll.unobserve(entry.target);
    }
  });
}, appearOptions);

faders.forEach(fader => {
  appearOnScroll.observe(fader);
});

// Smooth scroll for anchor links
const navLinks = document.querySelectorAll('a[href^="#"]');

navLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});

const textArray = [
  "Problem Solver",
  "Practical Coder",
  "AI Explorer",
  "Web Developer",
  "DSA Enthusiast",
];
let index = 0;
let charIndex = 0;
const speed = 80;
const pause = 500;
const element = document.getElementById("changing-text");

function typeEffect() {
  if (charIndex < textArray[index].length) {
    element.textContent += textArray[index].charAt(charIndex);
    charIndex++;
    setTimeout(typeEffect, speed);
  } else {
    setTimeout(eraseEffect, pause);
  }
}

function eraseEffect() {
  if (charIndex > 0) {
    element.textContent = textArray[index].substring(0, charIndex - 1);
    charIndex--;
    setTimeout(eraseEffect, speed / 2);
  } else {
    index = (index + 1) % textArray.length;
    setTimeout(typeEffect, speed);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Typing effect starter
  setTimeout(typeEffect, speed);

  // Hamburger menu toggle
  const hamburger = document.getElementById("hamburger");
  const mobileMenu = document.getElementById("mobileMenu");

  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", () => {
      mobileMenu.classList.toggle("active");
    });
  }
});

// Scroll-triggered navbar background
window.addEventListener("scroll", function () {
  const navbar = document.querySelector(".navbar");
  if (window.scrollY > 30) {
    navbar.classList.add("scrolled");
  } else {
    navbar.classList.remove("scrolled");
  }
});

// ---- Stars canvas ----
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  initStars();
});

class Star {
  constructor() {
    this.reset();
  }

  reset() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.radius = Math.random() < 0.05 ? Math.random() * 3 + 2 : Math.random() * 1.5 + 0.5;
    this.opacity = Math.random();
    this.fade = Math.random() * 0.02 + 0.01;
  }

  update() {
    this.opacity += this.fade;
    if (this.opacity <= 0 || this.opacity >= 1) this.fade *= -1;
  }

  draw() {
    ctx.beginPath();
    const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * 2);
    gradient.addColorStop(0, `rgba(100,150,255,${this.opacity})`);
    gradient.addColorStop(0.5, `rgba(100,150,255,${this.opacity * 0.5})`);
    gradient.addColorStop(1, `rgba(0,0,0,0)`);
    ctx.fillStyle = gradient;
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

let stars = [];

function initStars() {
  stars = [];
  for (let i = 0; i < 250; i++) {
    stars.push(new Star());
  }
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  stars.forEach((star) => {
    star.update();
    star.draw();
  });
  requestAnimationFrame(animate);
}

initStars();
animate();

// ---- Certificate Slider ----
let slides = document.querySelectorAll('.certificate-slide');
let currentSlide = 0;
let sliderInterval;

function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.toggle('active', i === index);
  });
}

function startSlider() {
  sliderInterval = setInterval(() => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }, 2000);
}

function stopSlider() {
  clearInterval(sliderInterval);
}

const certSlider = document.querySelector('.certificate-slider');
if (certSlider) {
  certSlider.addEventListener('mouseenter', () => {
    stopSlider();
    certSlider.classList.add('hovered');
  });
  certSlider.addEventListener('mouseleave', () => {
    startSlider();
    certSlider.classList.remove('hovered');
  });
  showSlide(currentSlide);
  startSlider();
}

// ---- GitHub hover cards ----
document.querySelectorAll('.github-card').forEach(card => {
  const desc = card.querySelector('.github-description');
  const originalText = desc.innerHTML;
  const hoverText = card.getAttribute('data-hovertext');

  card.addEventListener('mouseenter', () => {
    desc.textContent = hoverText;
  });
  card.addEventListener('mouseleave', () => {
    desc.innerHTML = originalText;
  });
});

// ---- Contact Form ----
const contactForm = document.getElementById("contactForm");
if (contactForm) {
  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("contactName").value.trim();
    const email = document.getElementById("contactEmail").value.trim();
    const message = document.getElementById("contactMessage").value.trim();

    if (!name || !email || !message) {
      alert("Please fill out all fields.");
      return;
    }

    // Save to Firestore
    if (typeof firebase !== 'undefined') {
      firebase.firestore().collection("messages").add({
        name: name,
        email: email,
        message: message,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
      }).then(() => {
        alert("Message sent successfully!");
        contactForm.reset();
      }).catch((error) => {
        alert("Failed to send message: " + error.message);
      });
    } else {
      alert("Message received! I'll get back to you soon.");
      contactForm.reset();
    }
  });
}

// ---- App Launcher ----
function toggleAppMenu() {
  const menu = document.getElementById('appMenu');
  if (menu) menu.classList.toggle('hidden');
}

document.addEventListener('click', function (event) {
  const launcher = document.querySelector('.app-launcher');
  const menu = document.getElementById('appMenu');
  if (launcher && menu && !launcher.contains(event.target)) {
    menu.classList.add('hidden');
  }
});

// ---- Blinking New Apps ----
document.addEventListener("DOMContentLoaded", function () {
  const icon = document.getElementById('app-icon');
  const text = document.getElementById('app-text');

  if (icon && text) {
    setInterval(() => {
      icon.style.display = 'none';
      text.style.display = 'inline';
      text.classList.add('blink-once');
      setTimeout(() => {
        text.classList.remove('blink-once');
        text.style.display = 'none';
        icon.style.display = 'inline';
      }, 1000);
    }, 5000);
  }

  // ---- AI Chat Panel ----
  const toggle = document.getElementById("ai-toggle");
  const panel  = document.getElementById("ai-panel");
  const body   = document.getElementById("ai-body");
  const input  = document.getElementById("ai-input");
  const send   = document.getElementById("ai-send");
  const modeBtn= document.getElementById("ai-mode");
  const typingIndicator = document.getElementById("ai-typing");

  if (!toggle || !panel || !body || !input || !send || !modeBtn) return;

  let open = false;
  let mode = "site";
  const history = [];

  const addBubble = (text, who) => {
    const b = document.createElement("div");
    b.className = "ai-bubble " + (who === "user" ? "ai-user" : "ai-bot");
    b.textContent = text;
    body.appendChild(b);
    body.scrollTop = body.scrollHeight;
  };

  const AI_URL = "https://chat-skqgszo5sa-uc.a.run.app";

  async function sendMessage(msg, addToHistory = false) {
    const payload = { message: msg };
    if (addToHistory) {
      payload.history = history;
      payload.mode = mode;
    }
    const res = await fetch(AI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Server error: " + res.status);
    const text = await res.text();
    if (!text) return "No reply.";
    try {
      const data = JSON.parse(text);
      return data.reply || "No reply.";
    } catch {
      return text;
    }
  }

  const sendMsg = async () => {
    const textVal = input.value.trim();
    if (!textVal) return;
    input.value = "";
    addBubble(textVal, "user");
    try {
      if (typingIndicator) typingIndicator.style.display = "block";
      const reply = await sendMessage(textVal, true);
      if (typingIndicator) typingIndicator.style.display = "none";
      addBubble(reply, "bot");
      history.push({ role: "user", content: textVal });
      history.push({ role: "assistant", content: reply });
      if (history.length > 12) history.splice(0, history.length - 12);
    } catch (err) {
      if (typingIndicator) typingIndicator.style.display = "none";
      addBubble("Error: " + err.message, "bot");
    }
  };

  toggle.addEventListener("click", () => {
    open = !open;
    panel.style.display = open ? "flex" : "none";
    panel.setAttribute("aria-hidden", String(!open));
    if (open) input.focus();
  });

  document.addEventListener("click", (e) => {
    if (!panel.contains(e.target) && !toggle.contains(e.target)) {
      open = false;
      panel.style.display = "none";
      panel.setAttribute("aria-hidden", "true");
    }
  });

  send.addEventListener("click", sendMsg);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMsg();
  });

  modeBtn.addEventListener("click", () => {
    mode = mode === "site" ? "general" : "site";
    modeBtn.textContent = "Mode: " + (mode === "site" ? "Site" : "General");
  });

  // Jumping AI icon
  const aiIcon = document.getElementById("ai-toggle");
  if (aiIcon) {
    setInterval(() => {
      aiIcon.classList.add("jump");
      setTimeout(() => aiIcon.classList.remove("jump"), 600);
    }, 4000);
  }
});

// ---- Firebase Auth & Login ----
// ⚠️ IMPORTANT: Set Firebase Security Rules in Firebase Console
// to restrict read/write access. Never expose admin SDK keys.
const firebaseConfig = {
  apiKey: "AIzaSyAtMfnVtNFF0mxCx79XyHSy4oMgqEcC4Oo",
  authDomain: "arun-portfolio-a3b35.firebaseapp.com",
  projectId: "arun-portfolio-a3b35",
  storageBucket: "arun-portfolio-a3b35.firebasestorage.app",
  messagingSenderId: "675276232971",
  appId: "1:675276232971:web:c80d5646bd5a121320aa0e"
};

// Initialize Firebase only once
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

const auth = firebase.auth();
const db = firebase.firestore();

const loginButtons = document.querySelectorAll(".login-btn");
const modal = document.getElementById("authModal");
const modalTitle = document.getElementById("modalTitle");
const toggleMode = document.getElementById("toggleMode");
const submitBtn = document.getElementById("submitBtn");
const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");
const phoneField = document.getElementById("phoneField");
const signupPasswords = document.getElementById("signupPasswords");
const createPassword = document.getElementById("createPassword");
const confirmPassword = document.getElementById("confirmPassword");

let isLogin = true;

loginButtons.forEach(btn => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    modal.classList.remove("hidden");
  });
});

modal?.addEventListener("click", (e) => {
  if (e.target === modal) modal.classList.add("hidden");
});

toggleMode.addEventListener("click", () => {
  isLogin = !isLogin;
  modalTitle.textContent = isLogin ? "Login" : "Sign Up";
  submitBtn.textContent = isLogin ? "Login" : "Sign Up";
  toggleMode.textContent = isLogin ? "Sign Up" : "Login";
  phoneField.classList.toggle("hidden", isLogin);
  signupPasswords.classList.toggle("hidden", isLogin);
  passwordInput.style.display = isLogin ? "block" : "none";
});

submitBtn.addEventListener("click", () => {
  const email = emailInput.value.trim();

  if (isLogin) {
    const password = passwordInput.value.trim();
    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }
    auth.signInWithEmailAndPassword(email, password)
      .then(() => { window.location.href = "welcome.html"; })
      .catch((error) => { alert("Login failed: " + error.message); });
  } else {
    const phone = document.getElementById("phoneInput").value.trim();
    const password = createPassword.value.trim();
    const confirm = confirmPassword.value.trim();

    if (!email || !phone || !password || !confirm) {
      alert("Please fill all fields.");
      return;
    }
    if (phone.length !== 10 || isNaN(phone)) {
      alert("Please enter a valid 10-digit phone number.");
      return;
    }
    if (password !== confirm) {
      alert("Passwords do not match.");
      return;
    }

    auth.createUserWithEmailAndPassword(email, password)
      .then((userCredential) => {
        const uid = userCredential.user.uid;
        return db.collection("users").doc(uid).set({ email: email, phone: phone });
      })
      .then(() => {
        alert("Account created! You can now log in.");
        toggleMode.click();
      })
      .catch((error) => { alert("Signup failed: " + error.message); });
  }
});

// Google Sign-In
document.getElementById("google-signin-btn").addEventListener("click", function () {
  const provider = new firebase.auth.GoogleAuthProvider();
  firebase.auth().signInWithPopup(provider)
    .then((result) => {
      const modal = document.getElementById("authModal");
      if (modal) modal.classList.add("hidden");
      showLoginPopup("Successfully Logged In", false);
      setTimeout(() => { window.location.href = "dashboard.html"; }, 2000);
    })
    .catch((error) => {
      showLoginPopup("Login Failed", true);
    });
});

function showLoginPopup(message, isError) {
  const popup = document.getElementById("loginPopup");
  if (!popup) return;
  popup.textContent = message;
  popup.classList.remove("hidden");
  popup.classList.add("show");
  popup.classList.toggle("error", isError);
  setTimeout(() => {
    popup.classList.remove("show");
    setTimeout(() => popup.classList.add("hidden"), 300);
  }, 2000);
}

// Auth State Change
auth.onAuthStateChanged((user) => {
  const defaultNav = document.getElementById("defaultNav");
  const loggedInNav = document.getElementById("loggedInFeatures");
  const loginBtn = document.querySelector(".login-btn");
  const logoutButtons = document.querySelectorAll(".logout-btn");
  const path = window.location.pathname;

  if (user) {
    defaultNav?.classList.add("hidden");
    loggedInNav?.classList.remove("hidden");
    loginBtn?.classList.add("hidden");

    logoutButtons.forEach((btn) => {
      if (!btn.hasAttribute("listener")) {
        btn.setAttribute("listener", "true");
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          const confirmLogout = window.confirm("Do you really want to logout?");
          if (confirmLogout) {
            auth.signOut().then(() => {
              alert("Logged out successfully.");
              window.location.href = "index.html";
            });
          }
        });
      }
    });

    // Redirect logged-in user from index to dashboard
    if (path.includes("index.html") || path === "/" || path.endsWith("/")) {
      setTimeout(() => { window.location.href = "dashboard.html"; }, 500);
    }
  } else {
    defaultNav?.classList.remove("hidden");
    loggedInNav?.classList.add("hidden");
    loginBtn?.classList.remove("hidden");
    logoutButtons.forEach((btn) => { btn.removeAttribute("listener"); });
  }
});

// ---- View Counter ----
const viewDocRef = db.collection("analytics").doc("visitCount");

async function trackAndDisplayViewCount() {
  try {
    await viewDocRef.set(
      { count: firebase.firestore.FieldValue.increment(1) },
      { merge: true }
    );
    const docSnap = await viewDocRef.get();
    const count = docSnap.data().count;

    const viewDiv = document.getElementById("visitCount");
    const viewNum = document.getElementById("viewNumber");

    if (viewNum) viewNum.innerText = count;
    if (viewDiv) {
      viewDiv.style.display = "block";
      viewDiv.classList.remove("visit-counter");
      void viewDiv.offsetWidth;
      viewDiv.classList.add("visit-counter");
      setTimeout(() => {
        viewDiv.style.opacity = "0";
        setTimeout(() => { viewDiv.style.display = "none"; }, 500);
      }, 2500);
    }
  } catch (err) {
    console.error("View counter failed:", err);
  }
}

trackAndDisplayViewCount();
