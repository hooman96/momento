import React from 'react';

const PricingCard = () => {
  const plans = [
    {
      name: 'Free',
      price: '$19/month',
      description: 'For Individual Developers',
      features: [
        { name: 'Time-Trackers', available: true },
        { name: '5 Projects', available: true },
        { name: '10GB Storage', available: true },
        { name: 'Basic Support', available: true },
        { name: 'Advanced Analytics', available: false },
        { name: 'Custom Analytics', available: false },
      ],
      btn: "Start Free trial"
    },
    {
      name: 'Premium',
      price: '$49/month',
      description: 'Ideal for small teams',
      features: [
        { name: 'Time-Trackers', available: true },
        { name: '50 Projects', available: true },
        { name: '100GB Storage', available: true },
        { name: 'Priority Support', available: true },
        { name: 'Advanced Analytics', available: true },
        { name: 'Custom Analytics', available: false },
      ],
      btn: " Get Started "
    },
    {
      name: 'Unlimited',
      price: '$99/month',
      description: 'Enterprises and Startups',
      features: [
        { name: 'Time-Trackers', available: true },
        { name: 'Unlimited Projects', available: true },
        { name: '1TB Storage', available: true },
        { name: '24/7 Support', available: true },
        { name: 'Advanced Analytics', available: true },
        { name: 'Custom Analytics', available: true },
      ],
      btn: " Contact Us "
    },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-800">
      <div className="max-w-6xl w-full mx-4">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-gray-100">Pricing Plans</h1>
          <p className="mt-4 text-lg md:text-xl text-gray-700 dark:text-gray-300">
            Flexible pricing plans designed to grow with you.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-700 rounded-lg shadow-lg p-6   flex flex-col"
            >

              <div className='grid grid-cols-4 ' >
                <div></div>
                <div> <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-gray-100">{plan.name}</h2></div>


              </div>
              <div className='grid grid-cols-1 ' >

                <div className='items-center justify-center flex ' ><p className="text-lg mb-2 text-gray-700 dark:text-gray-300">{plan.description}</p></div>
              </div>



              <p className="text-xl  flex justify-center mt-8   font-semibold mb-2 text-gray-900 dark:text-gray-100">{plan.price}</p>
              <ul className="mb-4 items-center grid grid-cols-3  justify-center   text-gray-700 dark:text-gray-300 flex-grow mt-10 ">
                <div></div>
                <div>
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center mb-2">
                      {feature.available ? (
                        <svg
                          className="w-6 h-6 text-green-500 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      ) : (
                        <svg
                          className="w-6 h-6 text-red-500 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      )}
                      {feature.name}
                    </li>
                  ))}
                </div>
                <div></div>
              </ul>
              <button className="mt-auto w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition duration-300">
                {plan.btn}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PricingCard;


