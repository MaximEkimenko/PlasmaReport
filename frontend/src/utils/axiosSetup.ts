import axios from "axios";
import { getTokenFromStore, clearStore } from "./local-storage";
import {endpoints} from "./authorization"
import { NavigateFunction } from "react-router-dom";
import {BASE_URL} from "./urls"



export const apiClient = axios.create({
    baseURL: BASE_URL,
    //настройка того, что при отправке массива экземпляр не будет добавлять кавдратные спобки к параметру
    // fio_doers= вместо fio_doers[]= для массивов
    paramsSerializer: params => {
        return Object.entries(params)
          .map(([key, value]) => {
            if (Array.isArray(value)) {
              return value.map(item => `${key}=${encodeURIComponent(item)}`).join('&');
            }
            // не нужно добавлять параметр если его значение ubdefined, это может привести к ошибке на сервере
            if (value !== undefined) {
            return `${key}=${encodeURIComponent(value)}`;
            }
          })
          .join('&');
      }
});


let navigateFunction: NavigateFunction | null = null;

export const setupInterceptors = (navigate?:NavigateFunction) => {
    if (navigate) {
        navigateFunction = navigate;
    }
    apiClient.interceptors.request.use(
        (config) => {
            const token = getTokenFromStore();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    apiClient.interceptors.response.use(
        (response) => response,
        (error) => {
            // Токен недействителен или истек
            if (error.response && error.response.status === 401) {
                clearStore(); // Удаляем токен из хранилища
                if (navigateFunction) navigateFunction(endpoints.LOGIN); // Перенаправляем пользователя на страницу логина
            }
            return Promise.reject(error);
        }
    );
};