exports.handler = async (event, context) => {
  process.env.DJANGO_SETTINGS_MODULE = 'app.conf.production.settings';
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'text/plain' },
    body: 'Django serverless function stub is active.'
  };
}; 