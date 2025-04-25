import { UserType, UserRolesType, UserIndexRolesType } from "../pages/Login/Login.types";

export const roleStrings = {
    USER: "Пользователь",
    ADMIN: "Администратор",
    TECHMAN: "Технолог",
    MASTER: "Мастер",
    OPERATOR: "Оператор",
    LOGIST: "Логист",
} as const;

export const roles: Record<UserRolesType, UserIndexRolesType> = {
    Пользователь: "USER",
    Администратор: "ADMIN",
    Технолог: "TECHMAN",
    Мастер: "MASTER",
    Оператор: "OPERATOR",
    Логист: "LOGIST",
} as const;


export const getUserRole = (user: UserType): UserIndexRolesType => { 
    const role = roles[user?.role]
    return role? role: "USER" satisfies UserIndexRolesType
}
export const endpoints = {
    TECHMAN: "/techman",
    MASTER: "/master",
    OPERATOR: "/operator",
    LOGIST: "/logist",
    LOGIN: "/login",
    MAIN_REPORT: "/report",
    DETAIL_REPORT: "details",
    ADD_OPERATOR: "/add-operator",
} as const;

type EndpointValues = (typeof endpoints)[keyof typeof endpoints];

export type EndpointData = { endpoint: EndpointValues; name: string };

export const appMenuItems: Record<keyof typeof endpoints, EndpointData> = {
    TECHMAN: { endpoint: endpoints.TECHMAN, name: "Технолог" },
    MASTER: { endpoint: endpoints.MASTER, name: "Мастер" , },
    OPERATOR: { endpoint: endpoints.OPERATOR, name: "Оператор" },
    LOGIST: { endpoint: endpoints.LOGIST, name: "Логист" },
    LOGIN: { endpoint: endpoints.LOGIN, name: "Логин" },
    MAIN_REPORT: { endpoint: endpoints.MAIN_REPORT, name: "Отчет" },
    ADD_OPERATOR: { endpoint: endpoints.ADD_OPERATOR, name: "Добавить оператора" },
};



export const allowedEndpoints: Record<UserIndexRolesType, EndpointData[]> = {
    USER: [appMenuItems.MAIN_REPORT],
    ADMIN: [
        appMenuItems.TECHMAN,
        appMenuItems.MASTER,
        appMenuItems.ADD_OPERATOR,
        appMenuItems.OPERATOR,
        appMenuItems.LOGIST,
        appMenuItems.MAIN_REPORT,
    ],
    TECHMAN: [appMenuItems.TECHMAN, appMenuItems.MAIN_REPORT],
    MASTER: [appMenuItems.MASTER, appMenuItems.ADD_OPERATOR, appMenuItems.OPERATOR, appMenuItems.MAIN_REPORT],
    OPERATOR: [appMenuItems.OPERATOR, appMenuItems.MAIN_REPORT],
    LOGIST: [appMenuItems.LOGIST, appMenuItems.MAIN_REPORT],
};

export const getUserEndpoints = (user: UserType | undefined) => {
    if (user) return allowedEndpoints[roles[user.role]];
    return [appMenuItems.MAIN_REPORT];
};

export const getDefaultPage = (user: UserType | undefined) => {
    return getUserEndpoints(user)[0].endpoint;
};

/**
 * Для подтверждения доступа к ресурсу проверяется, чтобы начальная часть алреса совпадала с одним
 * из адресов, доступных для данного пользователя. Эта проверка нужна когда пользователь переходит
 * к конкретной программе, и в конце адреса дописывается произвольный суффикс.
 * @param user  - текущий пользователь
 * @param endpoint - строка с текущим адресом в браузере
 * @returns
 */
export const isEndpointPermitted = (user: UserType | undefined, endpoint: string) => {
    const endpoints = getUserEndpoints(user);
    const isPermitted = endpoints.some((permitted) => {
        const tempalte = new RegExp(permitted.endpoint);
        return endpoint.match(tempalte);
    });

    return isPermitted;
};
