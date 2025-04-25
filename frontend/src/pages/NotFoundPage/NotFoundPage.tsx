import { useLocation } from "react-router-dom";

const NotFoundPage = () => {
    const params = useLocation();
    console.log(params);
    return <h1>Страница не найдена</h1>;
};

export default NotFoundPage;
