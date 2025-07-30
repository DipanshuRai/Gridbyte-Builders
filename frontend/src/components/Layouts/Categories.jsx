import mobiles from '../../assets/images/Categories/phone.png';
import fashion from '../../assets/images/Categories/fashion.png';
import electronics from '../../assets/images/Categories/electronics.png';
import home from '../../assets/images/Categories/home.png';
import travel from '../../assets/images/Categories/travel.png';
import appliances from '../../assets/images/Categories/appliances.png';
import furniture from '../../assets/images/Categories/furniture.png';
import beauty from '../../assets/images/Categories/beauty.png';
import grocery from '../../assets/images/Categories/grocery.png';
import { Link } from 'react-router-dom';

const catNav = [
    { name: "Mobiles", icon: mobiles },
    { name: "Fashion", icon: fashion },
    { name: "Electronics", icon: electronics },
    { name: "Home", icon: home },
    { name: "Travel", icon: travel },
    { name: "Appliances", icon: appliances },
    { name: "Furniture", icon: furniture },
    { name: "Beauty, Toys & More", icon: beauty },
    { name: "Grocery", icon: grocery },
];

const Categories = () => {
    return (
        <section className="hidden sm:block bg-white mt-4 mb-4 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between py-2 space-x-4 overflow-x-auto scrollbar-hide flex-nowrap">
                    {catNav.map((item, i) => (
                        <Link
                            to={`/products?category=${item.name}`}
                            key={i}
                            className="flex flex-col items-center justify-center flex-shrink-0 w-28 p-2 group"
                        >
                            <div className="h-30 w-30 p-1">
                                <img
                                    draggable="false"
                                    className="h-full w-full object-contain transition-transform duration-300 ease-in-out group-hover:scale-110"
                                    src={item.icon}
                                    alt={item.name}
                                />
                            </div>
                            <span className="text-sm text-center text-gray-800 font-medium transition-colors duration-200 group-hover:text-primary-blue">
                                {item.name}
                            </span>
                        </Link>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Categories;