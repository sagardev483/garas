// main.js

document.addEventListener('DOMContentLoaded', function() {
  console.log('Custom JS loaded successfully!');

  // Navbar background change on scroll
  let navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled');
    } else {
      navbar.classList.remove('navbar-scrolled');
    }
  });

  // Simulate subscription form success
  let subscriptionForm = document.querySelector('.subscription-form');
  if (subscriptionForm) {
    subscriptionForm.addEventListener('submit', function(e) {
      e.preventDefault();
      alert('Thank you for subscribing!');
      subscriptionForm.reset();
    });
  }

  // Smooth scroll for anchor links
  let anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      let target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});
