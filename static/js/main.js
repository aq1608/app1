// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Image selection for questionnaire (future enhancement)
function selectImage(element) {
    // Remove selection from all images
    document.querySelectorAll('.image-option').forEach(img => {
        img.classList.remove('selected');
    });
    
    // Add selection to clicked image
    element.classList.add('selected');
}

// Existing code...

// Like post functionality
function likePost(postId) {
    fetch(`/forum/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`likes-${postId}`).textContent = data.likes;
    })
    .catch(error => console.error('Error:', error));
}

// Chatbot functionality (placeholder for now)
function openChatbot() {
    alert('Chatbot feature coming soon! This will open an AI assistant to help you.');
    // Later we'll implement a modal with chatbot interface
}

// Star rating functionality
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.feedback-stars .star');
    let selectedRating = 5; // Default 5 stars
    
    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            selectedRating = index + 1;
            updateStarDisplay();
        });
        
        star.addEventListener('mouseover', function() {
            updateStarDisplay(index + 1);
        });
    });
    
    document.querySelector('.feedback-stars').addEventListener('mouseleave', function() {
        updateStarDisplay();
    });
    
    function updateStarDisplay(hoverRating = selectedRating) {
        stars.forEach((star, index) => {
            if (index < hoverRating) {
                star.style.opacity = '1';
                star.style.transform = 'scale(1.1)';
            } else {
                star.style.opacity = '0.3';
                star.style.transform = 'scale(1)';
            }
        });
    }
    
    // Initialize star display
    updateStarDisplay();
});

// Auto-expand textarea
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Mobile-friendly touch interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('.btn, .action-btn, .nav-item');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
});

// Existing code...

// Task completion functionality
function completeTask(taskId) {
    fetch(`/complete-task/${taskId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success modal
            document.getElementById('points-earned').textContent = data.points_earned;
            document.getElementById('modal-total-points').textContent = data.total_points;
            document.getElementById('successModal').style.display = 'flex';
            
            // Update UI
            updateTaskUI(taskId);
            updatePointsDisplay(data.total_points);
            updateProgress();
            
            // Confetti effect
            createConfetti();
        } else {
            alert(data.error || 'Task could not be completed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
    });
}

function updateTaskUI(taskId) {
    // Find the task item and mark as completed
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(item => {
        const button = item.querySelector(`button[onclick="completeTask(${taskId})"]`);
        if (button) {
            item.classList.remove('available');
            item.classList.add('completed');
            
            // Replace button with checkmark
            const checkbox = item.querySelector('.task-checkbox');
            checkbox.innerHTML = '✅';
            
            // Update points display
            const pointsEl = item.querySelector('.task-points');
            pointsEl.classList.add('earned');
        }
    });
}

function updatePointsDisplay(newTotal) {
    const pointsDisplay = document.getElementById('user-points');
    if (pointsDisplay) {
        // Animate the number change
        const currentPoints = parseInt(pointsDisplay.textContent);
        animateNumber(pointsDisplay, currentPoints, newTotal);
    }
}

function updateProgress() {
    // Update task counter
    const completedTasks = document.querySelectorAll('.task-item.completed').length;
    const totalTasks = document.querySelectorAll('.task-item').length;
    
    const counter = document.querySelector('.task-counter');
    if (counter) {
        counter.textContent = `${completedTasks}/${totalTasks}`;
    }
    
    // Update progress bar
    const progressFill = document.querySelector('.progress-section .progress-fill');
    if (progressFill) {
        const percentage = (completedTasks / totalTasks) * 100;
        progressFill.style.width = `${percentage}%`;
    }
    
    // Update progress text
    const progressText = document.querySelector('.progress-section p');
    if (progressText) {
        progressText.textContent = `${completedTasks} of ${totalTasks} tasks completed`;
    }
}

function animateNumber(element, start, end) {
    const duration = 1000; // 1 second
    const increment = (end - start) / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

function closeModal() {
    document.getElementById('successModal').style.display = 'none';
}

function createConfetti() {
    // Simple confetti effect
    const colors = ['#667eea', '#764ba2', '#28a745', '#ffc107', '#dc3545'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        createConfettiPiece(colors[Math.floor(Math.random() * colors.length)]);
    }
}

function createConfettiPiece(color) {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${color};
        top: -10px;
        left: ${Math.random() * 100}vw;
        z-index: 10000;
        pointer-events: none;
        border-radius: 50%;
    `;
    
    document.body.appendChild(confetti);
    
    // Animate falling
    const animation = confetti.animate([
        { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
        { transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`, opacity: 0 }
    ], {
        duration: Math.random() * 2000 + 1000,
        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });
    
    animation.onfinish = () => confetti.remove();
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
});