export type UserRolesType = "Пользователь" | "Администратор" | "Технолог" | "Мастер" | "Оператор" | "Логист";
export type UserIndexRolesType = "USER" | "ADMIN" | "TECHMAN" | "MASTER" | "OPERATOR" | "LOGIST";

export type UserType = {
    id: number;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
    is_verified: boolean;
    first_name: string;
    last_name: string;
    role: UserRolesType;
};
