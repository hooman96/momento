
 

const Hero2 = () => {



    return (

        <>

            <div className="min-h-screen  flex items-center justify-center bg-gray-100 dark:bg-gray-800 " >

                <div className=" container mx-auto px-4 py-8 grid grid-rows-2  text-black " >

                    <div className="items-center justify-center mb-10 " >

                        <h1 className="  font-bold text-5xl flex items-center justify-center  " > You build.</h1>
                        <h1 className=" flex items-center justify-center font-bold text-4xl mt-4 " >We migrate</h1>
                        <p className=" flex items-center justify-center mt-5 " >Engineers' time matters. Focus on your product while
                            we help you adopt the cutting-edge stack.
                        </p>
                    </div>
                    <div className="grid grid-cols-3 mt-10 " >
                        <div className="grid grid-rows-2" >
                            <div className="font-bold  text-2xl  flex items-center justify-center " > Reach us via Email </div>
                            <div className="font-normal text-xl  flex items-center justify-center "  >
                                <button className="mt-auto w-1/2 height-1/2  rounded-full bg-black text-white py-2  hover:bg-gray-800 transition duration-300">
                               Mail
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-rows-2" >
                            <div className="font-bold  text-2xl  flex items-center justify-center " > Chat With Us </div>
                            <div className="font-normal text-xl  flex items-center justify-center " >
                            <button className="mt-auto w-1/2 height-1/2  rounded-full bg-black text-white py-2  hover:bg-gray-800 transition duration-300">
                                  Join Slack
                                </button>
                            </div>
                        </div>
                        <div className="grid grid-rows-2" >
                            <div className="font-bold  text-2xl  flex items-center justify-center " > Hop a quick call for demo </div>
                            <div className="font-normal text-xl  flex items-center justify-center " > 
                            <button className="mt-auto w-1/2 height-1/2  rounded-full bg-black text-white py-2  hover:bg-gray-800 transition duration-300">
                                  Book a call
                                </button> </div>
                        </div>




                    </div>


                </div>

            </div>

        </>
    )


}


export default Hero2