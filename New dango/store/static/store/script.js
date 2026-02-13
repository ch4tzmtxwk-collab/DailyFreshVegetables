document.addEventListener('DOMContentLoaded', () => {
    updateTotal();
});

function getWeightMultiplier(weightStr) {
    if (weightStr === '250g') return 0.25;
    if (weightStr === '500g') return 0.5;
    if (weightStr === '1kg') return 1;
    if (weightStr === '2kg') return 2;
    if (weightStr === '3kg') return 3;
    if (weightStr === '4kg') return 4;
    if (weightStr === '5kg') return 5;
    return 0; // Default or "Select Weight"
}

function toggleCustomQty(select) {
    const wrapper = select.nextElementSibling;
    if (select.value === 'custom') {
        wrapper.style.display = 'flex';
        wrapper.querySelector('.custom-qty-input').focus();
    } else {
        wrapper.style.display = 'none';
        wrapper.querySelector('.custom-qty-input').value = '';
    }
    updateTotal();
}

function updateTotal() {
    let total = 0;
    const cards = document.querySelectorAll('.product-card');

    cards.forEach(card => {
        const priceText = card.querySelector('.price-tag').textContent;
        const basePrice = parseFloat(priceText.replace(/[^\d.]/g, ''));

        const weightSelect = card.querySelector('.quantity-select');
        let weightMultiplier = 0;

        if (weightSelect.value === 'custom') {
            const customInput = card.querySelector('.custom-qty-input');
            weightMultiplier = parseFloat(customInput.value) || 0;
        } else {
            weightMultiplier = getWeightMultiplier(weightSelect.value);
        }

        if (weightMultiplier > 0) {
            total += basePrice * weightMultiplier;
        }
    });

    document.querySelector('.amount').textContent = '₹' + total.toFixed(2);
}

// Add event listeners to selects to update total when weight changes
document.querySelectorAll('.quantity-select').forEach(select => {
    select.addEventListener('change', updateTotal);
});

function placeOrder() {
    const form = document.querySelector('#order-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const userDetails = {
        fullName: form.querySelector('[name="full_name"]').value,
        phoneNumber: form.querySelector('[name="phone_number"]').value,
        email: form.querySelector('[name="email"]').value,
        address: form.querySelector('[name="address"]').value
    };

    const cartItems = [];
    document.querySelectorAll('.product-card').forEach(card => {
        const weightSelect = card.querySelector('.quantity-select');
        const productName = card.querySelector('h3')?.textContent || 'Unknown Product';
        const priceText = card.querySelector('.price-tag')?.textContent || '₹0';
        const basePrice = parseFloat(priceText.replace(/[^\d.]/g, '') || '0');
        const unit = card.querySelector('.unit-label')?.textContent || 'kg';

        let finalQty = "";
        let finalPrice = 0;

        if (weightSelect.value === 'custom') {
            const customInput = card.querySelector('.custom-qty-input');
            const qtyVal = parseFloat(customInput.value) || 0;
            if (qtyVal > 0) {
                finalQty = `${qtyVal} ${unit}`;
                finalPrice = basePrice * qtyVal;
            }
        } else if (weightSelect.value !== 'Select Weight' && weightSelect.value !== '') {
            const weightVal = getWeightMultiplier(weightSelect.value);
            finalQty = weightSelect.value;
            finalPrice = basePrice * weightVal;
        }

        if (finalQty) {
            cartItems.push({
                id: card.dataset.productId,
                name: productName,
                quantity: finalQty,
                price: finalPrice.toFixed(2)
            });
        }
    });

    if (cartItems.length === 0) {
        alert('❌ Please select products (weight or custom qty) before placing an order.');
        return;
    }

    const totalAmount = parseFloat(document.querySelector('.amount')?.textContent.replace(/[^\d.]/g, '') || '0');

    const orderData = {
        userDetails,
        cartItems,
        totalAmount
    };

    console.log('Sending Order Data:', orderData);

    // Send data to backend
    fetch('/submit_order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(orderData)
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                console.error('Server Error:', data);
                throw new Error(data.message || 'Server returned 400');
            }
            return data;
        })
        .then(data => {
            if (data.status === 'success') {
                // Show Success Modal
                const successModal = document.getElementById('successModal');
                const successOrderId = document.getElementById('successOrderId');
                if (successModal && successOrderId) {
                    successOrderId.textContent = '#' + data.order_id;
                    successModal.style.display = 'flex';
                }

                form.reset();
                document.querySelectorAll('.quantity-select').forEach(select => select.value = 'Select Weight');
                document.querySelectorAll('.custom-qty-wrapper').forEach(w => w.style.display = 'none');
                updateTotal();

                // Automatic redirect after 60 seconds if not closed manually
                setTimeout(() => {
                    if (document.getElementById('successModal').style.display === 'flex') {
                        closeSuccessModal();
                    }
                }, 60000);
            } else {
                alert('❌ Error placing order:\n' + data.message);
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            alert('❌ Error placing order: ' + error.message);
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showPreview() {
    const form = document.querySelector('#order-form');

    // Get form data
    const fullName = form.querySelector('[name="full_name"]').value;
    const phoneNumber = form.querySelector('[name="phone_number"]').value;
    const email = form.querySelector('[name="email"]').value;
    const address = form.querySelector('[name="address"]').value;

    // Get cart items
    const cartItems = [];
    document.querySelectorAll('.product-card').forEach(card => {
        const weightSelect = card.querySelector('.quantity-select');
        const productName = card.querySelector('h3')?.textContent || 'Unknown Product';
        const priceText = card.querySelector('.price-tag')?.textContent || '₹0';
        const basePrice = parseFloat(priceText.replace(/[^\d.]/g, '') || '0');
        const unit = card.querySelector('.unit-label')?.textContent || 'kg';

        let finalQty = "";
        let finalPrice = 0;

        if (weightSelect.value === 'custom') {
            const customInput = card.querySelector('.custom-qty-input');
            const qtyVal = parseFloat(customInput.value) || 0;
            if (qtyVal > 0) {
                finalQty = `${qtyVal} ${unit}`;
                finalPrice = basePrice * qtyVal;
            }
        } else if (weightSelect.value !== 'Select Weight' && weightSelect.value !== '') {
            const weightVal = getWeightMultiplier(weightSelect.value);
            finalQty = weightSelect.value;
            finalPrice = basePrice * weightVal;
        }

        if (finalQty) {
            cartItems.push({
                name: productName,
                quantity: finalQty,
                price: finalPrice.toFixed(2)
            });
        }
    });

    if (cartItems.length === 0) {
        alert('🛒 Your cart is empty. Please select a weight or enter custom qty for the products you want!');
        return;
    }

    const totalAmount = parseFloat(document.querySelector('.amount')?.textContent.replace('₹', '') || '0');

    // Populate preview modal
    document.getElementById('previewName').textContent = fullName || '(Not provided yet)';
    document.getElementById('previewPhone').textContent = phoneNumber || '(Not provided yet)';
    document.getElementById('previewEmail').textContent = email || '(None)';
    document.getElementById('previewAddress').textContent = address || '(Not provided yet)';
    document.getElementById('previewTotal').textContent = totalAmount.toFixed(2);

    const itemsHTML = cartItems.map((item, index) => `
        <div style="padding: 0.8rem 0; border-bottom: ${index === cartItems.length - 1 ? 'none' : '1px solid #f0f0f0'}; display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <p style="margin: 0; font-weight: 600; color: #1b4d3e;">${index + 1}. ${item.name}</p>
                <p style="margin: 0.2rem 0 0 0; color: #666; font-size: 0.85rem;">${item.quantity}</p>
            </div>
            <p style="margin: 0; color: #27ae60; font-weight: 700; min-width: 80px; text-align: right;">₹${item.price}</p>
        </div>
    `).join('');

    document.getElementById('previewItems').innerHTML = itemsHTML;
    document.getElementById('previewModal').style.display = 'block';
}

function closePreview() {
    document.getElementById('previewModal').style.display = 'none';
}

function placeOrderFromPreview() {
    closePreview();
    placeOrder();
}

function closeSuccessModal() {
    const successModal = document.getElementById('successModal');
    if (successModal) {
        successModal.style.display = 'none';
    }
    // Redirection to my orders using the phone number from the form
    const phoneInput = document.querySelector('input[name="phone_number"]');
    const phoneValue = phoneInput ? phoneInput.value : '';
    window.location.href = '/my-orders/?phone=' + encodeURIComponent(phoneValue);
}

function dismissSuccessModal() {
    const successModal = document.getElementById('successModal');
    if (successModal) {
        successModal.style.display = 'none';
    }
}
