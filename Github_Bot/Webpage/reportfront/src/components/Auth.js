import '../App.css';
import React, { useEffect, useState } from "react";
import Report from './Report';
import seek_logo from "../seek_rats.png";
import github_login from "../github_img.png"

function Auth() {
    const queryString = require('query-string');
    const parsed = queryString.parse(window.location.search);

    const client_id = "Iv1.562a74542a3983be"
    const redirect_uri = window.location.origin + window.location.pathname //TODO: Get it from config
    var auth_url = "https://github.com/login/oauth/authorize?client_id="
    auth_url = auth_url.concat(client_id)
    auth_url = auth_url.concat("&redirect_uri=")
    auth_url = auth_url.concat(redirect_uri)
    console.log(auth_url)

    // If there is a code query assume they have went through github authentication and show them report page. Auth and token will be checked on report page.
    if (parsed["code"]) {
        return (
            <div>
                <Report auth_url_json={parsed}/>
            </div>
        )
    }
    else {
        return (
        
        <div class="centered">
            <div aclass="centered">
                <img class="centered" src={seek_logo} alt="seek rats logo" width="200px" /> 
                <h2>Code Review Report. Sign in to proceed. </h2>
                <p>
                    <a href={auth_url.concat(window.location.search)}>
                    <img src={github_login}></img> </a>
                </p>
            </div>
        </div>  
    )
    }
}
export default Auth;