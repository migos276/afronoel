// ========================================
// AfroNoël - Main JavaScript
// ========================================

// Get CSRF Token
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Add to Cart
function addToCart(productId, quantity = 1, size = "", color = "") {
  fetch("/api/cart/add/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: quantity,
      size: size,
      color: color,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateCartBadge(data.cart_count)
        showNotification(data.message, "success")
      } else {
        showNotification(data.error || "Erreur", "error")
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      showNotification("Une erreur est survenue", "error")
    })
}

// Update Cart Badge
function updateCartBadge(count) {
  let badge = document.getElementById("cart-badge")
  const cartIcon = document.querySelector(".cart-icon")

  if (count > 0) {
    if (!badge) {
      badge = document.createElement("span")
      badge.id = "cart-badge"
      badge.className = "cart-badge"
      cartIcon.appendChild(badge)
    }
    badge.textContent = count
  } else if (badge) {
    badge.remove()
  }
}

// Show Notification
function showNotification(message, type = "success") {
  // Remove existing notification
  const existing = document.querySelector(".notification")
  if (existing) existing.remove()

  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.innerHTML = `
        <i class="fas fa-${type === "success" ? "check-circle" : "exclamation-circle"}"></i>
        <span>${message}</span>
    `

  document.body.appendChild(notification)

  // Animate in
  setTimeout(() => notification.classList.add("show"), 10)

  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove("show")
    setTimeout(() => notification.remove(), 300)
  }, 3000)
}

// Add notification styles dynamically
const notificationStyles = document.createElement("style")
notificationStyles.textContent = `
    .notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #165b33;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transform: translateX(120%);
        transition: transform 0.3s ease;
        z-index: 9999;
    }
    .notification.show {
        transform: translateX(0);
    }
    .notification-error {
        background: #c41e3a;
    }
`
document.head.appendChild(notificationStyles)

// Mobile menu toggle
document.addEventListener("DOMContentLoaded", () => {
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
})
