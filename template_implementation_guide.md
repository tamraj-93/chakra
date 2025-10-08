# Template-Based Consultation Implementation Guide

This guide explains how to integrate the template-based consultation components into the Chakra application.

## Overview

We've created several components and enhanced existing services to support template-based consultations in the Chakra frontend:

1. Enhanced `ChatBoxComponent` to support template progress and structured input
2. Extended `ConsultationService` with template consultation methods
3. Updated `TemplateService` to fetch consultation templates
4. Created new components:
   - `TemplateStageProgressComponent`
   - `TemplateSelectionComponent`
   - `TemplateConsultationComponent`

## Integration Steps

### 1. Update Angular Module

First, update the app module to declare and export the new components:

```typescript
// In app.module.ts
import { TemplateStageProgressComponent } from './components/template-stage-progress/template-stage-progress.component';
import { TemplateSelectionComponent } from './components/template-selection/template-selection.component';
import { TemplateConsultationComponent } from './components/template-consultation/template-consultation.component';

@NgModule({
  declarations: [
    // ...existing components
    TemplateStageProgressComponent,
    TemplateSelectionComponent,
    TemplateConsultationComponent
  ],
  // ...other module configuration
})
export class AppModule { }
```

### 2. Add Routing

Update the routing configuration to include the new template-based consultation routes:

```typescript
// In app-routing.module.ts
import { TemplateSelectionComponent } from './components/template-selection/template-selection.component';
import { TemplateConsultationComponent } from './components/template-consultation/template-consultation.component';

const routes: Routes = [
  // ...existing routes
  { 
    path: 'templates', 
    component: TemplateSelectionComponent,
    canActivate: [AuthGuard] // If you have authentication
  },
  {
    path: 'templates/:templateId',
    component: TemplatePreviewComponent, // If you have a preview component
    canActivate: [AuthGuard]
  },
  {
    path: 'consultation/:sessionId',
    component: TemplateConsultationComponent,
    canActivate: [AuthGuard]
  }
];
```

### 3. Update Navigation

Add links to the template section in your main navigation:

```typescript
// In navbar.component.ts template
<li class="nav-item">
  <a class="nav-link" routerLink="/templates" routerLinkActive="active">
    <i class="bi bi-file-earmark-text"></i> Templates
  </a>
</li>
```

### 4. Ensure Backend API Support

The frontend components assume the following API endpoints are available:

- `GET /api/consultation/templates` - List all consultation templates
- `GET /api/consultation/templates/{id}` - Get a specific template by ID
- `POST /api/consultation/chat?template_id={id}` - Start a template consultation
- `POST /api/consultation/chat?session_id={id}` - Send a message in a consultation
- `GET /api/consultation/sessions/{id}` - Get session details
- `GET /api/consultation/sessions/{id}/messages` - Get messages for a session
- `GET /api/consultation/sessions/{id}/progress` - Get template progress for a session

### 5. Testing the Implementation

To test the template-based consultation flow:

1. Start the application and navigate to `/templates`
2. Select a template from the list to start a consultation
3. Follow the prompts through each stage
4. Verify that:
   - Progress indicators update correctly
   - Stage transitions are clear
   - Structured input works when applicable
   - Final summary includes all provided information

## Responsive Design Notes

These components are designed to be responsive, with special considerations for mobile devices:

- The template progress sidebar can be toggled on/off on smaller screens
- Template cards stack vertically on mobile
- Input fields expand to full width
- Template selection filters adapt to smaller screens

## Customization Options

You can customize the look and feel of these components by:

1. Updating the CSS variables in your global stylesheet
2. Modifying the component styles directly
3. Extending the template progress tracking with additional indicators

## Backend Implementation Considerations

The backend needs to support:

1. Storing template definitions with stages
2. Tracking session state with current stage information
3. Processing structured input
4. Generating appropriate prompts for each stage
5. Providing progress information with each response

## Next Steps for Enhancement

Potential future enhancements to consider:

1. Template preview functionality
2. Template creation/editing UI
3. Export results to PDF/Word
4. Template favoriting and rating system
5. Analytics on template usage and completion rates