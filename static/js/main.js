// Main JavaScript file for ReseñasPro

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add loading state to buttons when clicked
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Cargando...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Initialize star rating for review forms if present
    initStarRating();
    
    // Initialize product image gallery if present
    initProductGallery();
});

/**
 * Initialize star rating functionality
 */
function initStarRating() {
    const ratingContainers = document.querySelectorAll('.rating-container');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.rating-star');
        const ratingInput = container.querySelector('.rating-input');
        const ratingDisplay = container.querySelector('.rating-display');
        
        if (!stars.length || !ratingInput) return;
        
        // Set initial state based on input value
        const initialRating = parseFloat(ratingInput.value);
        if (initialRating) {
            updateStars(stars, initialRating);
            if (ratingDisplay) {
                ratingDisplay.textContent = initialRating.toFixed(1);
            }
        }
        
        // Star hover effect
        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                const rating = parseFloat(this.getAttribute('data-rating'));
                highlightStars(stars, rating);
            });
            
            star.addEventListener('mouseout', function() {
                const currentRating = parseFloat(ratingInput.value);
                if (currentRating) {
                    updateStars(stars, currentRating);
                } else {
                    stars.forEach(s => s.classList.remove('active', 'half'));
                }
            });
            
            star.addEventListener('click', function() {
                const rating = parseFloat(this.getAttribute('data-rating'));
                ratingInput.value = rating.toFixed(1);
                updateStars(stars, rating);
                
                if (ratingDisplay) {
                    ratingDisplay.textContent = rating.toFixed(1);
                }
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                ratingInput.dispatchEvent(event);
            });
        });
    });
}

/**
 * Update star display based on rating value
 */
function updateStars(stars, rating) {
    const fullRating = Math.floor(rating);
    const hasHalf = rating % 1 !== 0;
    
    stars.forEach(star => {
        const starRating = parseInt(star.getAttribute('data-rating'));
        
        star.classList.remove('active', 'half');
        
        if (starRating <= fullRating) {
            star.classList.add('active');
        } else if (hasHalf && starRating === fullRating + 1) {
            star.classList.add('half');
        }
    });
}

/**
 * Highlight stars on hover
 */
function highlightStars(stars, rating) {
    stars.forEach(star => {
        const starRating = parseInt(star.getAttribute('data-rating'));
        
        if (starRating <= rating) {
            star.classList.add('active');
            star.classList.remove('half');
        } else {
            star.classList.remove('active', 'half');
        }
    });
}

/**
 * Initialize product image gallery
 */
function initProductGallery() {
    const mainImage = document.getElementById('main-image');
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    
    if (!mainImage || !thumbnails.length) return;
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Update main image
            mainImage.src = this.getAttribute('data-src');
            
            // Update active class
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Handle like/dislike product functionality with AJAX
 */
function likeProduct(productId, type) {
    fetch(`/productos/${productId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `tipo=${type}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update UI
            const likeBtn = document.getElementById('like-btn');
            const dislikeBtn = document.getElementById('dislike-btn');
            const likesCount = document.getElementById('likes-count');
            const dislikesCount = document.getElementById('dislikes-count');
            
            if (data.action === 'added') {
                // Added a new like/dislike
                if (type === 'like') {
                    likeBtn.classList.add('btn-primary');
                    likeBtn.classList.remove('btn-outline-primary');
                    dislikeBtn.classList.remove('btn-danger');
                    dislikeBtn.classList.add('btn-outline-danger');
                } else {
                    dislikeBtn.classList.add('btn-danger');
                    dislikeBtn.classList.remove('btn-outline-danger');
                    likeBtn.classList.remove('btn-primary');
                    likeBtn.classList.add('btn-outline-primary');
                }
            } else if (data.action === 'removed') {
                // Removed an existing like/dislike
                if (type === 'like') {
                    likeBtn.classList.remove('btn-primary');
                    likeBtn.classList.add('btn-outline-primary');
                } else {
                    dislikeBtn.classList.remove('btn-danger');
                    dislikeBtn.classList.add('btn-outline-danger');
                }
            } else if (data.action === 'changed') {
                // Changed from like to dislike or vice versa
                if (type === 'like') {
                    likeBtn.classList.add('btn-primary');
                    likeBtn.classList.remove('btn-outline-primary');
                    dislikeBtn.classList.remove('btn-danger');
                    dislikeBtn.classList.add('btn-outline-danger');
                } else {
                    dislikeBtn.classList.add('btn-danger');
                    dislikeBtn.classList.remove('btn-outline-danger');
                    likeBtn.classList.remove('btn-primary');
                    likeBtn.classList.add('btn-outline-primary');
                }
            }
            
            // Update counts
            if (likesCount && data.likes_count) {
                likesCount.textContent = data.likes_count;
            }
            if (dislikesCount && data.dislikes_count) {
                dislikesCount.textContent = data.dislikes_count;
            }
        } else {
            // Handle error
            console.error('Error:', data.message);
            
            // Check if user needs to login
            if (data.error === 'login_required') {
                window.location.href = `/auth/login?next=/productos/${productId}`;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/**
 * Update review rating via AJAX
 */
function updateReviewRating(reviewId, rating) {
    fetch(`/resenas/actualizar-calificacion/${reviewId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `calificacion=${rating}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the UI
            const ratingDisplay = document.querySelector(`#review-${reviewId} .rating-display`);
            const starText = document.querySelector(`#review-${reviewId} .star-text`);
            
            if (ratingDisplay) {
                ratingDisplay.textContent = rating;
            }
            
            if (starText && data.estrellas) {
                starText.innerHTML = data.estrellas;
            }
            
            // Show success message
            const messageContainer = document.querySelector(`#review-${reviewId} .rating-message`);
            if (messageContainer) {
                messageContainer.textContent = 'Calificación actualizada correctamente';
                messageContainer.classList.add('text-success');
                
                // Hide message after 3 seconds
                setTimeout(() => {
                    messageContainer.textContent = '';
                    messageContainer.classList.remove('text-success');
                }, 3000);
            }
        } else {
            // Handle error
            console.error('Error:', data.message);
            
            // Show error message
            const messageContainer = document.querySelector(`#review-${reviewId} .rating-message`);
            if (messageContainer) {
                messageContainer.textContent = data.message || 'Error al actualizar la calificación';
                messageContainer.classList.add('text-danger');
                
                // Hide message after 3 seconds
                setTimeout(() => {
                    messageContainer.textContent = '';
                    messageContainer.classList.remove('text-danger');
                }, 3000);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}