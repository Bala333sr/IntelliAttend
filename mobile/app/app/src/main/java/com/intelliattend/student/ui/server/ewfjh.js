import React from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { 
    Home, 
    HelpCircle, 
    Bell, 
    Settings, 
    ChevronDown, 
    Play, 
    StopCircle,
    Pause,
    RefreshCw,
    CheckCircle,
    XCircle,
    Clock,
    BarChart2,
    Wifi,
    Bluetooth,
    Server,
    Shield,
    Eye,
    TrendingUp
} from "lucide-react";

export default function IntelliAttendDashboard() {
  const [activeRoom, setActiveRoom] = React.useState('Room A1');
  const [sessionStatus, setSessionStatus] = React.useState('stopped');

  const rooms = ['Room A1', 'Room B2', 'Room C3'];

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden">
        {/* Background blur effect */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-10"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80')"
          }}
        />
        
        {/* Header */}
        <header className="relative z-10 flex items-center justify-between px-8 py-6">
          <div className="flex items-center space-x-12">
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center space-x-2 cursor-pointer">
                  <div className="w-2 h-2 bg-white rotate-45"></div>
                  <span className="text-white font-bold text-xl tracking-wider">IntelliAttend</span>
                  <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-400/30 backdrop-blur-md">
                    Staging
                  </Badge>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>Version 1.2.5-beta | Click to return to dashboard</p>
              </TooltipContent>
            </Tooltip>
            
            <nav className="hidden md:flex space-x-8">
              <HeaderNavItem icon={Home} label="Dashboard" active />
              <HeaderNavItem icon={HelpCircle} label="Help & Contact" />
              <HeaderNavItem icon={Bell} label="Notifications" />
              <HeaderNavItem icon={Settings} label="Admin Settings" />
            </nav>
          </div>
          
          <div className="flex items-center space-x-6">
            {/* Room Selector moved to header */}
            <div className="flex space-x-2 bg-black/30 backdrop-blur-md rounded-full p-2 border border-white/10">
              {rooms.map((room) => (
                <button
                  key={room}
                  onClick={() => setActiveRoom(room)}
                  className={`px-4 py-2 rounded-full transition-all text-sm ${
                    activeRoom === room 
                      ? 'bg-white/20 text-white' 
                      : 'text-gray-400 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {room}
                </button>
              ))}
            </div>
            
            
            
            <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-md rounded-full">
              <span>CS101 - Section B</span>
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
            
            <Avatar className="w-12 h-12 border-2 border-white/20">
              <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&h=100&q=80" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="relative z-10 px-8 pb-8">
          <div className="grid grid-cols-12 gap-6 max-w-7xl mx-auto">
            
            {/* Faculty Details Panel - Now Expanded */}
            <div className="col-span-12 lg:col-span-8 relative">
              <div className="relative h-80 rounded-3xl overflow-hidden bg-gradient-to-r from-gray-800/80 to-gray-700/80 backdrop-blur-xl border border-white/10">
                <div 
                  className="absolute inset-0 bg-cover bg-center opacity-30"
                  style={{
                    backgroundImage: "url('https://images.unsplash.com/photo-1523050854058-8df90110c9d1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')"
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent" />
                
                {/* Session Controls Overlay */}
                <div className="absolute top-4 right-4 flex gap-2">
                  <Button size="sm" className="bg-white/20 backdrop-blur-md border-white/10 text-white hover:bg-white/30 rounded-full">
                    View Roster
                  </Button>
                  <Button size="sm" className="bg-white/20 backdrop-blur-md border-white/10 text-white hover:bg-white/30 rounded-full">
                    Session Log
                  </Button>
                  <Button size="sm" className="bg-white/20 backdrop-blur-md border-white/10 text-white hover:bg-white/30 rounded-full">
                    Timetable
                  </Button>
                </div>
                
                <div className="relative h-full flex flex-col justify-between p-8">
                  <div>
                    <div className="mb-4">
                      <h2 className="text-lg text-gray-300">Dr. Jane Doe</h2>
                      <p className="text-sm text-gray-400">Associate Professor, Computer Science</p>
                    </div>
                    <h1 className="text-4xl lg:text-5xl font-bold text-white leading-tight mb-2">
                      ADVANCED<br />
                      ALGORITHMS
                    </h1>
                    <p className="text-gray-300 mb-6">Session ID: S-A9B1C2 | Expected: 85 Students</p>
                  </div>
                  
                  {/* OTP Input with Dashed Placeholders */}
                  <div className="flex justify-end">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-2">
                        {Array.from({length: 6}).map((_, i) => (
                          <input
                            key={i}
                            type="text"
                            maxLength="1"
                            className="w-12 h-12 bg-white/20 border-2 border-dashed border-white/30 text-white text-center font-mono text-xl rounded-lg backdrop-blur-md focus:border-white focus:outline-none"
                            placeholder="_"
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Session Controls Card - Updated with Start Button */}
            <div className="col-span-12 lg:col-span-4">
              <div className="h-80 rounded-3xl bg-black/30 backdrop-blur-xl border border-white/10 p-6 flex flex-col justify-center">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-white text-xl font-bold">Session Controls</h3>
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-gray-400 rounded-full" />
                    <span className="text-gray-400 text-sm">Stopped</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <Button className="w-full bg-green-600 hover:bg-green-700 text-white backdrop-blur-md rounded-2xl py-4 text-base">
                    <Play className="mr-2 h-5 w-5" />
                    Start Session
                  </Button>
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/20 backdrop-blur-md rounded-2xl py-4 text-base">
                    <Pause className="mr-2 h-5 w-5" />
                    Pause Session
                  </Button>
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/20 backdrop-blur-md rounded-2xl py-4 text-base">
                    <RefreshCw className="mr-2 h-5 w-5" />
                    Restart Session
                  </Button>
                  <Button className="w-full bg-red-600/80 hover:bg-red-700 text-white backdrop-blur-md rounded-2xl py-4 text-base">
                    <StopCircle className="mr-2 h-5 w-5" />
                    Stop Session
                  </Button>
                </div>
              </div>
            </div>
            
            {/* Bottom Panels with New Distribution */}
            {/* Live Attendance Card - 50% width */}
            <div className="col-span-12 lg:col-span-6">
              <div className="h-64 rounded-3xl bg-black/30 backdrop-blur-xl border border-white/10 p-6 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white text-xl font-bold">Live Attendance</h3>
                  <Badge className="bg-green-500/20 text-green-400 border-green-400/30">
                    Active
                  </Badge>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    </div>
                    <p className="text-2xl font-bold text-green-400">68</p>
                    <p className="text-xs text-gray-400">Present</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Clock className="w-6 h-6 text-yellow-400" />
                    </div>
                    <p className="text-2xl font-bold text-yellow-400">5</p>
                    <p className="text-xs text-gray-400">Late</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                      <XCircle className="w-6 h-6 text-red-400" />
                    </div>
                    <p className="text-2xl font-bold text-red-400">12</p>
                    <p className="text-xs text-gray-400">Absent</p>
                  </div>
                </div>
                
                <div className="flex-grow bg-white/10 rounded-2xl p-3 backdrop-blur-md border border-white/10">
                  <div className="grid grid-cols-10 gap-1 h-full">
                    {Array.from({length: 100}).map((_, i) => (
                      <div 
                        key={i} 
                        className={`aspect-square rounded-sm ${
                          i < 68 ? 'bg-green-400' : 
                          i < 73 ? 'bg-yellow-400' : 
                          'bg-gray-600'
                        } opacity-80`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Analytics Card - 30% width */}
            <div className="col-span-12 lg:col-span-4">
              <div className="h-64 rounded-3xl bg-black/30 backdrop-blur-xl border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white text-xl font-bold">Analytics</h3>
                  <BarChart2 className="w-5 h-5 text-gray-400" />
                </div>
                
                <div className="mb-4">
                  <p className="text-gray-300 text-sm mb-2">Weekly Average</p>
                  <div className="flex items-center gap-2">
                    <div className="text-3xl font-bold text-white">88%</div>
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  </div>
                </div>
                
                <div className="h-16 bg-white/10 rounded-xl flex items-center justify-center">
                  <div className="flex space-x-2">
                    {[0.4, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7].map((height, i) => (
                      <div 
                        key={i} 
                        className="w-3 bg-blue-400 rounded-t"
                        style={{height: `${height * 40}px`}}
                      />
                    ))}
                  </div>
                </div>
                
                <div className="mt-4 flex justify-between text-xs">
                  <div>
                    <p className="text-gray-400">Anomalies</p>
                    <p className="font-bold text-red-400">3</p>
                  </div>
                  <Button size="sm" className="bg-white/20 hover:bg-white/30 text-white backdrop-blur-md rounded-full">
                    <Eye className="w-3 h-3 mr-1" />
                    View Details
                  </Button>
                </div>
              </div>
            </div>

            {/* System Health Card - 20% width, Simplified Icons */}
            <div className="col-span-12 lg:col-span-2">
              <div className="h-64 rounded-3xl bg-black/30 backdrop-blur-xl border border-white/10 p-6 flex flex-col">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-white text-lg font-bold">System Health</h3>
                  <Shield className="w-5 h-5 text-green-400" />
                </div>
                
                <div className="flex-grow flex flex-col justify-center space-y-6">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto cursor-pointer">
                        <Wifi className="w-8 h-8 text-green-400" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Wi-Fi: Excellent (12ms)</p>
                    </TooltipContent>
                  </Tooltip>
                  
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto cursor-pointer">
                        <Bluetooth className="w-8 h-8 text-blue-400" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>BLE Advertiser: Active</p>
                    </TooltipContent>
                  </Tooltip>
                  
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto cursor-pointer">
                        <Server className="w-8 h-8 text-gray-400" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Server Sync: 2s ago</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                
                <Button size="sm" className="w-full bg-white/20 hover:bg-white/30 text-white backdrop-blur-md rounded-xl mt-4">
                  Re-sync
                </Button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

const HeaderNavItem = ({ icon: Icon, label, active = false }) => (
  <Tooltip>
    <TooltipTrigger asChild>
      <button className={`text-sm transition-colors ${active ? 'text-white font-medium' : 'text-gray-300 hover:text-white'}`}>
        {label}
      </button>
    </TooltipTrigger>
    <TooltipContent>
      <p>{label}</p>
    </TooltipContent>
  </Tooltip>
);