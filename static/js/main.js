/* =========================================================
   LegalAwareKE — main.js
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    // --------------------------------------------------
    // 1. Clickable table rows
    // --------------------------------------------------
    document.querySelectorAll(".data-table tbody tr").forEach(function (row) {
        const link = row.querySelector("a.btn");
        if (link) {
            row.addEventListener("click", function (e) {
                if (e.target.tagName === "A" || e.target.tagName === "BUTTON") return;
                window.location.href = link.href;
            });
        }
    });

    // --------------------------------------------------
    // 2. Active nav link highlight
    // --------------------------------------------------
    const path = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(function (link) {
        if (link.getAttribute("href") === path) {
            link.classList.add("active");
        }
    });

    // --------------------------------------------------
    // 3. Scroll to top button
    // --------------------------------------------------
    const scrollBtn = document.createElement("button");
    scrollBtn.innerHTML = "↑";
    scrollBtn.setAttribute("aria-label", "Scroll to top");
    scrollBtn.style.cssText =
        "position:fixed;bottom:2rem;right:2rem;width:42px;height:42px;" +
        "border-radius:50%;border:none;background:#c9a84c;color:#0d1b2a;" +
        "font-size:1.2rem;cursor:pointer;display:none;z-index:999;" +
        "box-shadow:0 4px 12px rgba(0,0,0,0.2);font-weight:700;transition:opacity 0.3s;";
    document.body.appendChild(scrollBtn);

    window.addEventListener("scroll", function () {
        scrollBtn.style.display = window.scrollY > 400 ? "block" : "none";
    });
    scrollBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // --------------------------------------------------
    // 4. Auto-dismiss flash messages after 4 seconds
    // --------------------------------------------------
    document.querySelectorAll(".flash").forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = "opacity 0.5s";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 500);
        }, 4000);
    });

});
