import React, { useContext } from "react";
import styles from "./NavBar.module.css";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { Box, Button } from "@mui/material";
import LogoutButton from "../../components/LogoutButton/LogoutButton";
import { endpoints, getUserEndpoints } from "../../utils/authorization";
import { useAuth } from "../../hooks/use-auth";
import {BASE_URL} from "../../utils/urls"
const Navbar: React.FC = () => {

    const authContext = useAuth();
    if (!authContext) {
        throw new Error("Не определено значение для конекста авторизации");
    }
    const { currentUser } = authContext;
    const { pathname } = useLocation();
    const login = (
        <>
            <Link className={styles["login-container"]} to={endpoints.LOGIN}>
                <Button size="small" variant="contained">
                    войти
                </Button>
            </Link>
        </>
    );
    const logout = (
        <>
            <span style={{marginRight:10}}>
                {currentUser?.last_name} | {currentUser?.role}
            </span>
            <LogoutButton />
        </>
    );
    const authWidget = !currentUser ? pathname === endpoints.LOGIN ? <></> : login : logout;

    return (
        <>
            <nav>
                <ul className={styles.navbar}>
                    {getUserEndpoints(currentUser).map((item) => (
                        <li key={item.name}>
                            <NavLink
                                className={({ isActive }) => {
                                    return [styles["menu-link"], isActive ? styles.active : ""].join(" ");
                                }}
                                to={item.endpoint}
                            >
                                {item.name}
                            </NavLink>
                        </li>
                    ))}
                    
                    <a className = {styles["menu-link"]} href={`${BASE_URL}/instruction`} >Инструкция</a>
                    <li style={{flexGrow:1}}></li>
                    <li>{authWidget}</li>
                </ul>
                

            </nav>
            {/* <div className={styles.background}> */}
            <div >
            <Outlet/>
            </div>
        </>
    );
};

export default Navbar;
