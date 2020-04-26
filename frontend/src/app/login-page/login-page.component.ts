import { Component, OnInit } from '@angular/core';
import {AuthService} from '../auth.service'

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.scss']
})
export class LoginPageComponent implements OnInit {

  potentialUser = {
    email: '',
    password: '',
  }

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    this.authService.checkSessionCookie()
  }

  submitLogin(){
    console.log(this.potentialUser)
    this.authService.checkCredentials(this.potentialUser)
  }

}