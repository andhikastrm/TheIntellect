// js/slider.js
document.addEventListener("DOMContentLoaded", function () {
  const swiper = new Swiper(".fitur-swiper", {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 30,
    centeredSlides: true,
    autoplay: {
      speed: 800,
      delay: 4000,
      disableOnInteraction: false,
    },

    effect: "slide",               // atau coba "fade" / "cube" / "coverflow" kalau mau variasi
    fadeEffect: {                  // kalau pakai effect: "fade"
      crossFade: true
    },
    grabCursor: true,
    transitionTimingFunction: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
    
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      500: { slidesPerView: 1 },
      768: { slidesPerView: 2 },
      992: { slidesPerView: 3 },
    },
  });
});