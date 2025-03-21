// Add debug logging
console.log('Script loaded');

// Move fetchRestaurants to top for hoisting
function fetchRestaurants(page) {
    console.log('Fetching page:', page);
    fetch(`/api/restaurants?page=${page}&per_page=${perPage}`)
        .then(response => {
            console.log('Response received:', response);
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);
            const searchResults = document.getElementById('searchResults');
            const restaurantList = document.getElementById('restaurantList');
            const pagination = document.getElementById('pagination');
            
            if (searchResults) searchResults.style.display = 'none';
            if (restaurantList) {
                restaurantList.style.display = 'grid';
                if (data && data.restaurants) {
                    renderRestaurants(data.restaurants, 'restaurantList');
                    currentPage = data.page;
                    updatePagination(data.page, data.total);
                } else {
                    restaurantList.innerHTML = '<p>No restaurants found.</p>';
                }
            }
            if (pagination) pagination.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            const restaurantList = document.getElementById('restaurantList');
            if (restaurantList) {
                restaurantList.innerHTML = '<p>Error loading restaurants. Please try again later.</p>';
            }
        });
}

function renderRestaurants(restaurants, container = 'restaurantList') {
    console.log('Rendering restaurants:', restaurants);
    const list = document.getElementById(container);
    if (!list) {
        console.error(`Container ${container} not found`);
        return;
    }
    
    list.innerHTML = '';
    
    if (!Array.isArray(restaurants) || restaurants.length === 0) {
        list.innerHTML = '<div class="no-results">No restaurants found</div>';
        return;
    }

    restaurants.forEach(restaurant => {
        const card = document.createElement('div');
        card.className = 'search-result-card';
        card.innerHTML = `
            <img src="${restaurant["Image URL"] || '/static/placeholder.jpg'}" 
                 alt="${restaurant["Restaurant Name"]}" 
                 class="restaurant-image">
            <div class="restaurant-info">
                <h3>${restaurant["Restaurant Name"] || 'Unknown Restaurant'}</h3>
                <div class="search-result-details">
                    <p>${restaurant.Cuisines || 'Not specified'}</p>
                    <div class="rating">★ ${restaurant["Aggregate rating"] || 'N/A'}</div>
                    <div class="restaurant-features">
                        ${restaurant["Has Table booking"] === "Yes" ? 
                            '<span class="feature-tag">🪑 Table Booking</span>' : ''}
                        ${restaurant["Has Online delivery"] === "Yes" ? 
                            '<span class="feature-tag">🛵 Delivery</span>' : ''}
                    </div>
                    <div class="restaurant-price">
                        ${restaurant.Currency || ''} ${restaurant["Average Cost for two"] || 'N/A'} for two
                    </div>
                </div>
            </div>
        `;
        card.onclick = () => showRestaurantDetails(restaurant);
        list.appendChild(card);
    });
}

function showRestaurantDetails(restaurant) {
    console.log('Showing details for:', restaurant);
    const detailsContainer = document.getElementById('restaurantDetails');
    if (!detailsContainer) {
        console.error('Restaurant details container not found');
        return;
    }

    // Hide other containers
    document.getElementById('restaurantList').style.display = 'none';
    document.getElementById('pagination').style.display = 'none';
    if (document.getElementById('searchResults')) {
        document.getElementById('searchResults').style.display = 'none';
    }

    // Show and populate details
    detailsContainer.style.display = 'block';
    detailsContainer.innerHTML = `
        <div class="restaurant-detail-card">
            <img src="${restaurant["Image URL"] || '/static/placeholder.jpg'}" 
                 alt="${restaurant["Restaurant Name"]}" 
                 class="detail-image">
            <div class="detail-info">
                <h2>${restaurant["Restaurant Name"]}</h2>
                
                <div class="detail-rating">
                    <span>★ ${restaurant["Aggregate rating"] || 'N/A'}</span>
                    <span style="margin-left: 8px; font-size: 0.9em">${restaurant["Rating text"] || 'N/A'}</span>
                </div>

                <div class="detail-features">
                    ${restaurant["Has Table booking"] === "Yes" ? 
                        '<span class="feature-tag">🪑 Table Booking Available</span>' : ''}
                    ${restaurant["Has Online delivery"] === "Yes" ? 
                        '<span class="feature-tag">🛵 Online Delivery</span>' : ''}
                    <span class="feature-tag">💵 ${restaurant.Currency || ''} ${restaurant["Average Cost for two"] || 'N/A'} for two</span>
                </div>

                <div class="detail-meta">
                    <p><strong>Cuisine:</strong> ${restaurant.Cuisines || 'Not specified'}</p>
                    <p><strong>Votes:</strong> ${restaurant.Votes || '0'} reviews</p>
                    <p><strong>Locality:</strong> ${restaurant["Locality Verbose"] || 'N/A'}</p>
                </div>

                <p><strong>Address:</strong> ${restaurant.Address || 'N/A'}</p>
            </div>
        </div>
        <button onclick="hideRestaurantDetails()" class="back-button">
            ← Back to Restaurants
        </button>
    `;
}

function hideRestaurantDetails() {
    document.getElementById('restaurantDetails').style.display = 'none';
    document.getElementById('restaurantList').style.display = 'grid';
    document.getElementById('pagination').style.display = 'block';
}

let currentPage = 1;
const perPage = 10;

function updatePagination(page, total) {
    const totalPages = Math.ceil(total / perPage);
    document.getElementById('pageInfo').textContent = `Page ${page} of ${totalPages}`;
    
    // Enable/disable pagination buttons
    const prevButton = document.querySelector('.pagination button:first-child');
    const nextButton = document.querySelector('.pagination button:last-child');
    
    if (prevButton && nextButton) {
        prevButton.disabled = page <= 1;
        nextButton.disabled = page >= totalPages;
    }
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        fetchRestaurants(currentPage);
    }
}

function nextPage() {
    currentPage++;
    fetchRestaurants(currentPage);
}

function searchByLocation() {
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    const radius = document.getElementById('radius').value;
    if (!lat || !lon || !radius) {
        alert('Please enter latitude, longitude, and radius');
        return;
    }
    
    fetch(`/api/restaurants/nearby?lat=${lat}&lon=${lon}&radius=${radius}`)
        .then(response => response.json())
        .then(restaurants => {
            const list = document.getElementById('restaurantList');
            list.style.display = 'grid';
            if (restaurants.length > 0) {
                renderRestaurants(restaurants, 'restaurantList');
            } else {
                list.innerHTML = '<p>No restaurants found within the specified radius</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('restaurantList').innerHTML = '<p>Error loading results</p>';
        });
}

function searchRestaurants() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    fetch(`/api/restaurants/search?q=${query}`)
        .then(response => response.json())
        .then(restaurants => {
            document.getElementById('searchResults').style.display = 'none';
            document.getElementById('pagination').style.display = 'none';
            const restaurantList = document.getElementById('restaurantList');
            restaurantList.style.display = 'grid';
            if (restaurants.length > 0) {
                renderRestaurants(restaurants, 'restaurantList');
            } else {
                restaurantList.innerHTML = '<p>No restaurants found for "' + query + '".</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            document.getElementById('restaurantList').innerHTML = '<p>Error loading results.</p>';
        });
}

function renderRestaurantDetails(r, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="restaurant-detail-card">
            <img src="${r["Image URL"] || '/static/placeholder.jpg'}" 
                 alt="${r["Restaurant Name"]}" 
                 class="detail-image">
            <div class="detail-info">
                <h2>${r["Restaurant Name"]}</h2>
                
                <div class="detail-rating">
                    <span>★ ${r["Aggregate rating"] || 'N/A'}</span>
                    <span style="margin-left: 8px; font-size: 0.9em">${r["Rating text"] || 'N/A'}</span>
                </div>

                <div class="detail-features">
                    ${r["Has Table booking"] === "Yes" ? 
                        '<span class="feature-tag">🪑 Table Booking Available</span>' : ''}
                    ${r["Has Online delivery"] === "Yes" ? 
                        '<span class="feature-tag">🛵 Online Delivery</span>' : ''}
                    <span class="feature-tag">💵 ${r.Currency || ''} ${r["Average Cost for two"] || 'N/A'} for two</span>
                </div>

                <div class="detail-meta">
                    <p><strong>Cuisine:</strong> ${r.Cuisines || 'Not specified'}</p>
                    <p><strong>Votes:</strong> ${r.Votes || '0'} reviews</p>
                    <p><strong>Locality:</strong> ${r["Locality Verbose"] || 'N/A'}</p>
                </div>

                <p><strong>Address:</strong> ${r.Address || 'N/A'}</p>
            </div>
        </div>
        <button onclick="hideRestaurantDetails()" class="back-button">
            ← Back to Restaurants
        </button>
    `;
}

function hideRestaurantDetails() {
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('restaurantList').style.display = 'grid';
}