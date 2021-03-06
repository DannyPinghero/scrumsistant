/// <reference path="../../types/scrum-types.d.ts" />

import {BrowserModule} from '@angular/platform-browser'
import {NgModule} from '@angular/core'
import {FormsModule} from '@angular/forms'
import {HttpClientModule} from '@angular/common/http'

import {AppRoutingModule} from './app-routing.module'
import {AppComponent} from './app.component'
import {PointingComponent} from './pointing/pointing.component'
import {DashboardComponent} from './dashboard/dashboard.component'
import {StandupComponent} from './standup/standup.component'
import {NavComponent} from './nav/nav.component'
import {LoginPageComponent} from './login-page/login-page.component'
import {PmToolsComponent} from './pm-tools/pm-tools.component'
import {CurrentTeamComponent} from './current-team/current-team.component'

@NgModule({
  declarations: [
    AppComponent,
    PointingComponent,
    DashboardComponent,
    StandupComponent,
    NavComponent,
    LoginPageComponent,
    PmToolsComponent,
    CurrentTeamComponent,
  ],
  imports: [BrowserModule, AppRoutingModule, FormsModule, HttpClientModule],
  bootstrap: [AppComponent],
})
export class AppModule {}
