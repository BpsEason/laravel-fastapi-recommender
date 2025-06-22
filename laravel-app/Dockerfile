FROM php:8.2-fpm-alpine

WORKDIR /var/www/html

RUN apk add --no-cache \
    nginx \
    mysql-client \
    git \
    curl \
    supervisor \
    freetype-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    libwebp-dev \
    imagemagick-dev \
    autoconf \
    g++ \
    make \
    pcre-dev \
    # For Redis Extension
    redis \
    # For Bcrypt for password hashing (Laravel)
    php82-bcmath \
    # For pdo_mysql
    php82-pdo_mysql

RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-install pdo_mysql bcmath

# Install Redis PHP extension
RUN pecl install -o -f redis \
    && rm -rf /tmp/pear \
    && docker-php-ext-enable redis

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy only composer.json and composer.lock first to leverage Docker cache
COPY laravel-app/composer.json laravel-app/composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-scripts

COPY laravel-app .
# Copy custom nginx config
COPY laravel-app/docker/nginx/default.conf /etc/nginx/http.d/default.conf

# Set permissions for storage and bootstrap/cache
RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache \
    && chmod -R 775 /var/www/html/storage /var/www/html/bootstrap/cache

EXPOSE 80

CMD ["php-fpm"]
