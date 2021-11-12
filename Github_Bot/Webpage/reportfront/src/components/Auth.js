import logo from '../logo.svg';
import '../App.css';
import React, { useEffect, useState } from "react";
import Report from './Report';

function Auth() {
    const [authenticated, setAuth] = useState(0);


    if (authenticated === 1) {
        console.log(authenticated);
        return (
            <div>
                <Report/>
            </div>
        )
    } else {
        return (
            <div>
                <h1
                    onClick={() => setAuth(1)}
                > yo </h1>
            </div>
        )
    }
    
}
export default Auth;