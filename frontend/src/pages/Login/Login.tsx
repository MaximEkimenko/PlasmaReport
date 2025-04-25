import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import {
    Alert,
    Box,
    Button,
    FormControl,
    IconButton,
    InputAdornment,
    InputLabel,
    OutlinedInput,
    Snackbar,
    Stack,
    TextField,
    Typography,
} from "@mui/material";

import { getDefaultPage } from "../../utils/authorization.ts";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useAuth } from "../../hooks";
import { BASE_URL, urls } from "../../utils/urls.ts";

type loginResponse = { access_token: string; token_type: string };
type userLoginType = { username: string; password: string };

const Login = () => {
    const authContext = useAuth();
    if (!authContext) {
        throw new Error("Не определено значение для конекста авторизации");
    }
    const { currentUser, login } = authContext;

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const errorMessage = "Неверное имя пользователя или пароль.";
    const navigate = useNavigate();
    const [showPassword, setShowPassword] = React.useState(false);

    const handleClickShowPassword = () => setShowPassword((show) => !show);
    const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    const handleMouseUpPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    const handleLogin = async (userobj: userLoginType) => {
        try {
            // Отправка POST-запроса на сервер с использованием axios

            const response = await axios.post<loginResponse>(`${BASE_URL}/${urls.AUTH_LOGIN}`, userobj, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });
            const token = response.data.access_token;
            login(token);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 400) {
                    setOpenSnackbar(true);
                    console.log("ошибка авторизации");
                } else {
                    console.error("Ошибка в ходе авторизации:", error);
                }
            }
        }
    };

    useEffect(() => {
        if (currentUser) {
            navigate(getDefaultPage(currentUser)); // переход на дефолтный адрес после логина
        }
    }, [currentUser, navigate]);


    const handleSubmit = () => {
        handleLogin({ username, password });
    };


        const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
            if (event.key === "Enter") {
                handleSubmit();
            }
        };
    return (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 2,
                    mt: 1,
                    my: "auto",
                    width: 800,
                }}
            >
                <Typography variant="h5" align="center" gutterBottom>
                    Вход
                </Typography>

                <Stack sx={{ backgroundColor: "background.paper", borderRadius: 1, padding: 1, rowGap: 1 }}>
                    <TextField
                        name="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyDown={handleKeyDown}
                        label="Пользователь"
                        sx={{ m: 1, width: "300px" }}
                        variant="outlined"
                    />

                    <FormControl sx={{ m: 1, width: "300px" }} variant="outlined">
                        <InputLabel htmlFor="outlined-adornment-password">Пароль</InputLabel>
                        <OutlinedInput
                            id="outlined-adornment-password"
                            type={showPassword ? "text" : "password"}
                            name="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            onKeyDown={handleKeyDown}
                            endAdornment={
                                <InputAdornment position="end">
                                    <IconButton
                                        onClick={handleClickShowPassword}
                                        onMouseDown={handleMouseDownPassword}
                                        onMouseUp={handleMouseUpPassword}
                                        edge="end"
                                    >
                                        {showPassword ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            }
                            label="Пароль"
                        />
                    </FormControl>
                    <Button variant="contained" onClick={handleSubmit}>
                        {" "}
                        Войти
                    </Button>
                    <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={() => setOpenSnackbar(false)}>
                        <Alert
                            /*variant="filled"*/ onClose={() => setOpenSnackbar(false)}
                            severity="error"
                            sx={{ width: "100%" }}
                        >
                            {errorMessage}
                        </Alert>
                    </Snackbar>
                </Stack>

                {/* <Stack spacing={2}>
                    <Button
                        variant="contained"
                        onClick={() => handleLogin({ username: "dima@mail.ru", password: "1234" })}
                    >
                        {" "}
                        Войти админом
                    </Button>
                    <Button
                        variant="contained"
                        onClick={() => handleLogin({ username: "as@mail.ru", password: "1234" })}
                    >
                        {" "}
                        Войти мастером
                    </Button>
                    <Button
                        variant="contained"
                        onClick={() => handleLogin({ username: "vp@mail.ru", password: "1234" })}
                    >
                        {" "}
                        Войти оператором
                    </Button>
                </Stack> */}
            </Box>
        </Box>
    );
};

export default Login;
