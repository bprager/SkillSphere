FROM debian:bookworm

ENV NGINX_VERSION=1.26.0

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg build-essential libpcre3 libpcre3-dev zlib1g-dev libssl-dev \
    libxml2-dev libxslt1-dev libgd-dev libgeoip-dev libmaxminddb-dev \
    libperl-dev git unzip wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /usr/src

# Download NGINX
RUN curl -O http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar zxvf nginx-${NGINX_VERSION}.tar.gz && \
    rm nginx-${NGINX_VERSION}.tar.gz

# Clone third-party modules
RUN git clone https://github.com/openresty/headers-more-nginx-module.git && \
    git clone https://github.com/yaoweibin/nginx_upstream_check_module.git && \
    git clone https://github.com/openresty/echo-nginx-module.git && \
    git clone https://github.com/vision5/ngx_devel_kit.git && \
    git clone https://github.com/arut/nginx-dav-ext-module.git && \
    git clone https://github.com/kaltura/nginx-upload-module.git && \
    git clone https://github.com/FRiCKLE/ngx_cache_purge.git && \
    git clone https://github.com/leev/ngx_http_geoip2_module.git

# Build NGINX with modules
WORKDIR /usr/src/nginx-${NGINX_VERSION}
RUN ./configure \
    --prefix=/etc/nginx \
    --sbin-path=/usr/sbin/nginx \
    --modules-path=/usr/lib/nginx/modules \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --pid-path=/var/run/nginx.pid \
    --lock-path=/var/run/nginx.lock \
    --with-compat \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_auth_request_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_slice_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-http_perl_module=dynamic \
    --add-dynamic-module=../headers-more-nginx-module \
    --add-dynamic-module=../nginx_upstream_check_module \
    --add-dynamic-module=../echo-nginx-module \
    --add-dynamic-module=../nginx-dav-ext-module \
    --add-dynamic-module=../ngx_cache_purge \
    --add-dynamic-module=../ngx_http_geoip2_module \
    --add-dynamic-module=../ngx_devel_kit \
    --add-dynamic-module=../nginx-upload-module && \
    make -j$(nproc) && \
    make install

# Cleanup build deps
RUN apt-get purge -y build-essential git curl && \
    rm -rf /usr/src/*

# Prepare entrypoint
RUN mkdir -p /var/log/nginx /etc/nginx/conf.d /etc/nginx/modules-enabled

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]

