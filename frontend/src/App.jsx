import React, { useState, useEffect } from 'react';

// --- Helper Components ---

// An SVG component for the futuristic bus icon
const BusIcon = ({ isFound }) => (
    <svg className={`w-24 h-auto transition-all duration-300 ${isFound ? 'drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]' : ''}`} viewBox="0 0 200 100">
        <path d="M10 30 H180 A10 10 0 0 1 190 40 V80 H10 V30 Z" fill={isFound ? "#334155" : "#1e293b"} stroke={isFound ? "#fbbf24" : "#475569"} strokeWidth="3" />
        <path d="M15 30 L35 15 H175 V30 H15 Z" fill="#0f172a" />
        <rect x="40" y="35" width="125" height="20" fill="#0f172a" />
        <circle cx="50" cy="80" r="12" fill="#1e293b" stroke={isFound ? "#fbbf24" : "#475569"} strokeWidth="2"/>
        <circle cx="140" cy="80" r="12" fill="#1e293b" stroke={isFound ? "#fbbf24" : "#475569"} strokeWidth="2"/>
        <circle cx="165" cy="80" r="12" fill="#1e293b" stroke={isFound ? "#fbbf24" : "#475569"} strokeWidth="2"/>
        <path d="M70 60 L90 40 H105 L85 60 H70 Z" fill="#F97316" />
        <path d="M92 60 L112 40 H127 L107 60 H92 Z" fill="#7C3AED" />
        <path d="M114 60 L134 40 H149 L129 60 H114 Z" fill="#1E40AF" />
    </svg>
);

// Component for a standard parking spot
const StandardSpot = ({ spot, isFound }) => (
    <div className="relative flex flex-col items-center justify-center p-2 h-115 w-75">
        {/* Holographic Base */}
        <div className={`absolute bottom-0 w-full h-3/3 transition-colors duration-300 rounded-t-lg ${isFound ? 'bg-amber-400/10' : 'bg-cyan-400/10'}`}></div>
        <div className={`absolute bottom-0 w-full h-1 ${isFound ? 'bg-amber-400' : 'bg-cyan-400'} animate-pulse`}></div>
        
        {spot.actualBus && (
            <div className="relative z-10 flex flex-col items-center gap-2">
                <BusIcon isFound={isFound} />
                <span className="font-bold text-2xl">{spot.actualBus}</span>
            </div>
        )}
        <span className="absolute top-0 right-2 text-sm font-light text-slate-400">{spot.spotId}</span>
    </div>
);

// --- Main App Component ---

function App() {
    // State to hold the latest parking status from the backend
    const [parkingStatus, setParkingStatus] = useState([]);
    // State for the search input
    const [searchTerm, setSearchTerm] = useState('');
    // State for the live clock
    const [time, setTime] = useState(new Date());

    // This effect hook fetches data and updates the clock
    useEffect(() => {
        const fetchData = async () => {
            try {
                // This is the live API call to your backend server
                const response = await fetch('http://localhost:8000/api/status');
                const data = await response.json();
                
                // Update the dashboard with the REAL data from the server
                setParkingStatus(data);
            } catch (error) {
                console.error("Failed to fetch parking status:", error);
                // In case of an error, we can set it to an empty array
                setParkingStatus([]);
            }
        };

        fetchData(); // Initial fetch
        const dataInterval = setInterval(fetchData, 2000); // Fetch data every 2 seconds
        const timeInterval = setInterval(() => setTime(new Date()), 1000);

        return () => {
            clearInterval(dataInterval);
            clearInterval(timeInterval);
        };
    }, []); // The empty array ensures this effect runs only once on mount

    const occupiedSpots = parkingStatus.filter(s => s.actualBus).length;
    const totalSpots = parkingStatus.length;

    // Filter spots for each row
    const topRowSpots = parkingStatus.filter(spot => ['A1', 'A2'].includes(spot.spotId));
    const bottomRowSpots = parkingStatus.filter(spot => ['B1', 'B2', 'B3'].includes(spot.spotId));

    return (
        <div className="bg-slate-900 min-h-screen text-slate-200 font-sans flex p-4 lg:p-6 gap-6">
            {/* Sidebar */}
            <aside className="w-1/4 lg:w-1/5 bg-slate-900/50 border border-slate-700 rounded-lg flex flex-col p-6 space-y-8 shadow-2xl">
                <div className="text-center">
                    <h1 className="text-2xl font-bold text-cyan-400">Genius Garage</h1>
                    <p className="text-xs text-slate-500">Automated Parking System</p>
                </div>

                <div className="flex-grow space-y-6">
                    <div>
                        <label className="text-sm text-slate-400">Search Vehicle</label>
                        <input 
                            type="text" 
                            placeholder="Bus ID..." 
                            className="w-full bg-slate-800 border border-slate-600 text-white p-2 rounded-md mt-1 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div>
                        <h3 className="text-sm text-slate-400">System Status</h3>
                        <p className="text-lg font-semibold text-green-400 flex items-center gap-2">
                            <span className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
                            Operational
                        </p>
                    </div>
                    <div>
                        <h3 className="text-sm text-slate-400">Depot Capacity</h3>
                        <p className="text-lg font-semibold">{occupiedSpots} / {totalSpots} Occupied</p>
                    </div>
                </div>

                <div className="text-center text-slate-500">
                    <p className="text-lg font-mono">{time.toLocaleTimeString()}</p>
                    <p className="text-xs">{time.toLocaleDateString()}</p>
                </div>
            </aside>

            {/* Main Content */}
            <main className="w-3/4 lg:w-4/5 flex flex-col items-center justify-center gap-6 bg-slate-900/50 border border-slate-700 rounded-lg p-4">
                {/* Top Row */}
                <div className="flex justify-center gap-8">
                    {topRowSpots.map(spot => (
                        <StandardSpot 
                            key={spot.spotId} 
                            spot={spot} 
                            isFound={searchTerm && spot.actualBus?.includes(searchTerm)} 
                        />
                    ))}
                </div>
                {/* Bottom Row */}
                <div className="flex justify-center gap-8">
                    {bottomRowSpots.map(spot => (
                        <StandardSpot 
                            key={spot.spotId} 
                            spot={spot} 
                            isFound={searchTerm && spot.actualBus?.includes(searchTerm)} 
                        />
                    ))}
                </div>
            </main>
        </div>
    );
}

export default App;
