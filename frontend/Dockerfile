FROM node:20-bookworm

# Set the working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files and install dependencies
COPY package*.json ./

# Install dependencies as root
RUN pnpm install

# Copy the rest of your application code with correct ownership
COPY --chown=node:node . .

# Create start.sh with LF line endings and set permissions outside of volume mount
RUN printf "#!/bin/bash\n\npnpm run dev &\n\nnode watcher.js\n\nwait\n" > /usr/local/bin/start-app.sh && chmod +x /usr/local/bin/start-app.sh

# Switch to the non-root user
USER node

EXPOSE 3000

# Start the application
CMD ["/usr/local/bin/start-app.sh"]
