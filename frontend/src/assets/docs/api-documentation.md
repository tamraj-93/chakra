# Chakra API Documentation

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Refresh token

### Templates (SLA Templates)
- `GET /api/templates` - Get all SLA templates
- `GET /api/templates/{id}` - Get specific SLA template
- `POST /api/templates` - Create new SLA template
- `PUT /api/templates/{id}` - Update SLA template
- `DELETE /api/templates/{id}` - Delete SLA template

### Consultation Templates
- `GET /api/consultation_templates/templates` - Get all consultation templates
- `GET /api/consultation_templates/templates/{id}` - Get specific consultation template
- `POST /api/consultation_templates/templates` - Create new consultation template
- `PUT /api/consultation_templates/templates/{id}` - Update consultation template
- `DELETE /api/consultation_templates/templates/{id}` - Delete consultation template

### Consultation
- `POST /api/consultation/chat` - Send a message in consultation
- `GET /api/consultation/sessions` - Get all consultation sessions
- `GET /api/consultation/sessions/{id}` - Get specific consultation session
- `GET /api/consultation/sessions/{id}/messages` - Get messages for a session
- `GET /api/consultation/sessions/{id}/progress` - Get progress for a template consultation session

## Common Issues

### 404 Not Found on Template Endpoints
If you're getting a 404 Not Found error when accessing templates, check that you're using the correct endpoint:

- For SLA Templates: `/api/templates`
- For Consultation Templates: `/api/consultation_templates/templates` (not `/api/consultation/templates`)

### Authentication Issues
All API endpoints except `/api/auth/login` and `/api/auth/register` require authentication. Make sure to include a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

If you're getting "Not authenticated" errors, ensure that:
1. You're logged in
2. The token hasn't expired
3. The token is properly included in the request header

### CORS Issues
If you're getting CORS errors in the browser, ensure the backend is configured to allow requests from your frontend domain.