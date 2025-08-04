const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  // Set environment variables for Django
  process.env.DJANGO_SETTINGS_MODULE = 'app.conf.production.settings';
  process.env.PYTHONPATH = path.join(__dirname, '../../source');
  
  // Parse the request
  const { httpMethod, path: requestPath, queryStringParameters, body } = event;
  
  // Create a simple Django-like request object
  const djangoRequest = {
    method: httpMethod,
    path: requestPath,
    query: queryStringParameters || {},
    body: body || '',
    headers: event.headers || {}
  };
  
  try {
    // For now, return a simple response indicating Django is configured
    // In a real implementation, you would need to run Django via subprocess
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'text/html',
        'Access-Control-Allow-Origin': '*'
      },
      body: `
        <!DOCTYPE html>
        <html>
        <head>
          <title>StoneWalker - Django Backend</title>
        </head>
        <body>
          <h1>StoneWalker Django Backend</h1>
          <p>Request path: ${requestPath}</p>
          <p>Method: ${httpMethod}</p>
          <p>Django is configured and ready to handle requests.</p>
          <p>Note: This is a placeholder. For full Django functionality, consider using a different hosting platform like Heroku, Railway, or DigitalOcean.</p>
        </body>
        </html>
      `
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'text/plain'
      },
      body: `Error: ${error.message}`
    };
  }
}; 