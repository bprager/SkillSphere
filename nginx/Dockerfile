FROM nginx:1.25

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcre3-dev \
    zlib1g-dev \
    libssl-dev \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install GeoIP2 module
RUN cd /tmp && \
    git clone https://github.com/leev/ngx_http_geoip2_module.git && \
    cd ngx_http_geoip2_module && \
    git checkout 3.4 && \
    cd /tmp && \
    wget http://nginx.org/download/nginx-1.25.3.tar.gz && \
    tar -xzvf nginx-1.25.3.tar.gz && \
    cd nginx-1.25.3 && \
    ./configure --with-compat --add-dynamic-module=/tmp/ngx_http_geoip2_module && \
    make modules && \
    cp objs/ngx_http_geoip2_module.so /usr/lib/nginx/modules/ && \
    cd / && \
    rm -rf /tmp/*

# Create directory for GeoIP2 module
RUN mkdir -p /etc/nginx/modules && \
    echo "load_module /usr/lib/nginx/modules/ngx_http_geoip2_module.so;" > /etc/nginx/modules/geoip2.conf

# Include GeoIP2 module in main nginx.conf
RUN echo "include /etc/nginx/modules/*.conf;" >> /etc/nginx/nginx.conf 