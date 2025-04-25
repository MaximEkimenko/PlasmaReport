export const BASE_URL = "http://192.168.8.163:8000";

export const urls = {
    AUTH_LOGIN: "auth/login",
    AUTH_LOGOUT: "auth/logout",
    URL_AUTH_AUTHENTICATED: "auth/authenticated-route",
    AUTH_REGISTER: "auth/register",

    TECHMAN_GET_PROGRAMS: "techman/get_programs",
    TECHMAN_GET_PROGRAM_PARTS: "techman/get_program_parts",
    TECHMAN_GET_ORDERS: "techman/get_orders",
    TECHMAN_CREATE_PROGRAM_DATA: "techman/create_data",
    TECHMAN_UPDATE_PROGRAM_DATA: "techman/update_data",

    USER_ME: "user/me",

    MASTER_GET_PROGRAMS_AND_DOERS: "master/get_programs_for_assignment_and_doers",
    MASTER_ASSIGN_PROGRAMS: "master/assign_program",
    MASTER_GET_DOERS: "master/get_doers",
    MASTER_GET_PARTS_BY_PROGRAM_ID: "master/get_parts_by_program_id", //!!!!
    // MASTER_GET_PARTS_BY_STATUSES: "master/get_parts_by_statuses",

    OPERATOR_GET_MY_PROGRAMS: "operator/get_my_programs",
    OPERATOR_START_PROGRAM: "operator/start_program",
    OPERATOR_SET_MY_PARTS: "operator/this_is_my_parts",

    LOGIST_GET_PROGRAMS: "logist/get_programs_for_calculation",
    LOGIST_CALCULATE_PARTS: "logist/calculate_parts",

    REPORT_PARTS_FULL: "reports/parts_full",

    ORDER_GET_WO_DETAILS: "reports/get_wo_details",
};
