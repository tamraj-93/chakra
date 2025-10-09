import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { ConsultationComponent } from './pages/consultation/consultation.component';
import { TemplateGeneratorComponent } from './pages/template-generator/template-generator.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TemplateConsultationComponent } from './components/template-consultation/template-consultation.component';
import { TemplateListComponent } from './pages/template-list/template-list.component';
import { DebugToolsComponent } from './components/debug-tools/debug-tools.component';
import { SlaTemplateGeneratorComponent } from './components/sla-template-generator/sla-template-generator.component';
import { KnowledgeBaseComponent } from './pages/knowledge-base/knowledge-base.component';
import { MySLAsComponent } from './pages/my-slas/my-slas.component';
import { SlaDocumentComponent } from './pages/sla-document/sla-document.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { 
    path: 'consultation', 
    component: ConsultationComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'templates',
    component: TemplateListComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'template-consultation/:id', 
    component: TemplateConsultationComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'template-generator', 
    component: TemplateGeneratorComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'sla-template-generator', 
    component: SlaTemplateGeneratorComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'dev/debug',
    component: DebugToolsComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'knowledge-base',
    component: KnowledgeBaseComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'my-slas',
    component: MySLAsComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'sla-documents/:id',
    component: SlaDocumentComponent,
    canActivate: [AuthGuard]
  },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }