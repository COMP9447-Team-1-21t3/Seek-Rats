import logo from '../logo.svg';
import '../App.css';
import React, { useEffect, useState } from "react";
import Report from './Report';

function Auth() {
    const queryString = require('query-string');
    const [repo_url, setURL] = useState("") //Get from query string
    const [is_repo_valid, setValidCheck] = useState(false)
    const parsed = queryString.parse(window.location.search);

    const client_id = "bafc9bb95ef83e08ded6" //get from config
    const redirect_uri = "http://localhost:3000" //Get it from config

    if (parsed[repo_url]) {
        setURL(repo_url);
        setValidCheck(true);
        console.log(repo_url);
    }
    
    var auth_url = "https://github.com/login/oauth/authorize?client_id="
    auth_url = auth_url.concat(client_id)
    auth_url = auth_url.concat("&redirect_uri=")
    auth_url = auth_url.concat(redirect_uri)
    console.log(auth_url)

    if (parsed["code"]) {
        return (
            <div>
                <Report auth_url_json={parsed}/>
            </div>
        )
    }
     else {
        return (
            
            <div>
                {console.log(window.location.search)}
                {is_repo_valid ? 
                <a href={auth_url.concat(window.location.search)}>Login with Github</a> : <a>Need Repo Query</a>
                }      
                <a href={auth_url.concat(window.location.search)}>Login with Github</a>
            </div>  
             


        )
    }
    
}
export default Auth;