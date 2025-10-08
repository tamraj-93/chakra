import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommonModule } from '@angular/common';

// Pipes
import { StructuredDataPipe } from './shared/pipes/structured-data.pipe';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';

// Pages
import { HomeComponent } from './pages/home/home.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { ConsultationComponent } from './pages/consultation/consultation.component';
import { TemplateGeneratorComponent } from './pages/template-generator/template-generator.component';

// Components
import { ChatBoxComponent } from './components/chat-box/chat-box.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TemplatePreviewComponent } from './components/template-preview/template-preview.component';
import { ModalComponent } from './components/shared/modal/modal.component';
import { TemplateStageProgressComponent } from './components/template-stage-progress/template-stage-progress.component';
import { TemplateConsultationComponent } from './components/template-consultation/template-consultation.component';
import { TemplateListComponent } from './pages/template-list/template-list.component';
import { DebugToolsComponent } from './components/debug-tools/debug-tools.component';
import { SlaTemplateGeneratorComponent } from './components/sla-template-generator/sla-template-generator.component';
import { KnowledgeBaseComponent } from './pages/knowledge-base/knowledge-base.component';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    RegisterComponent,
    ConsultationComponent,
    TemplateGeneratorComponent,
    ChatBoxComponent,
    NavbarComponent,
    DashboardComponent,
    TemplatePreviewComponent,
    ModalComponent,
    TemplateStageProgressComponent,
    TemplateConsultationComponent,
    TemplateListComponent,
    DebugToolsComponent,
    SlaTemplateGeneratorComponent,
    KnowledgeBaseComponent,
    LoadingSpinnerComponent,
    StructuredDataPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    CommonModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

// TODO: Ensure animations are properly configured in Angular app
// - Make sure BrowserAnimationsModule is imported in app.module.ts
// - Use animation triggers in components with [@animationName]
// - Apply route animations with animation definitions in router outlet