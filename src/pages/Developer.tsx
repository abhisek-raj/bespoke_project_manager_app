import Footer from "../components/Footer";

const Developer = (props: any) => {
  return (
    <>
      <div className="flex justify-center mt-10">
        <div className="max-w-[800px] w-[90%] bg-slate-700 border-2 border-slate-500 rounded-xl p-8">
          <h1 className="text-4xl text-white font-bold text-center">Developer Dashboard</h1>
          <p className="text-gray-300 mt-4 text-center">
            This is the developer landing page. Add developer-specific tools here.
          </p>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default Developer;
