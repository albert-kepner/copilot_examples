fn main() {
    println!("Hello, the_lift");
    println!("{:?}", the_lift(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5));
}

fn the_lift(queues: &[Vec<u32>], capacity: u32) -> Vec<u32> {
    let mut lift_state: LiftState = LiftState::new(queues, capacity);
    let mut v: Vec<u32> = vec![];
    lift_state.stop_at_floor(0);
    v.push(0);
    while let Some(floor) = lift_state.next_floor() {
        // println!("floor = {}", floor);
        // Avoid pushing the same floor twice due to direction switch...
        if v[v.len() - 1] != floor {
            v.push(floor);
        }
    }
    // When there are no more requests the elevator stops on floor zero.
    if v[v.len() - 1] != 0 {
        v.push(0)
    }
    println!("{:?}", v);
    v
}

#[derive(Debug)]
enum Direction {
    Up,
    Down,
}

#[derive(Debug)]
struct LiftState {
    direction: Direction,
    capacity: u32,
    floor: u32,
    riders: Vec<u32>,
    queues: Vec<Vec<u32>>,
}

impl LiftState {
    pub fn new(queues: &[Vec<u32>], capacity: u32) -> Self {
        Self {
            direction: Direction::Up,
            capacity: capacity,
            floor: 0,
            riders: vec![],
            queues: queues.iter().cloned().collect(),
        }
    }

    fn next_floor(&mut self) -> Option<u32> {
        if let Some(floor) = self.find_next_stop_forward() {
            // println!(" find_next_stop_forward() {}, {:?}", floor, self.direction);
            self.stop_at_floor(floor);
            return Some(floor);
        } else  if let Some(floor) = self.find_stop_to_reverse() {
            // println!(" find_stop_to_reverse() floor = {}, {:?}", floor, self.direction);
            // We have established that a direction switch is required.
            match self.direction {
                Direction::Up => {
                    self.direction = Direction::Down;
                }
                Direction::Down => {
                    self.direction = Direction::Up;
                }
            }
            self.stop_at_floor(floor);
            return Some(floor);
        } else {
            // Switch directions to look for traffic going the other way, if any.
            match self.direction {
                Direction::Up => {
                    self.direction = Direction::Down;
                }
                Direction::Down => {
                    self.direction = Direction::Up;
                }
            }
            if let Some(floor) = self.find_stop_to_reverse() {
                // println!(" find_stop_to_reverse() floor = {}, {:?}", floor, self.direction);
                self.stop_at_floor(floor);
                return Some(floor);
            }
        }
        None
    }

    /// Assumption: We have not found any more passengers to assist
    /// traveling in the current direction. This function
    /// starts at one extreme floor.
    /// -- Top floor if currently going up or
    /// -- Bottom floor if currently going down.
    /// And then finds the closest floor needing a stop to 
    /// pick up or drop off passengers in the new direction
    fn find_stop_to_reverse(&self) -> Option<u32> {
        // println!("in find_stop_to_reverse direction = {:?}", self.direction);
        let mut floor: usize;
        match self.direction {   
            Direction::Up => {
                // work from the top floor down
                floor = self.queues.len();
                while floor > 0 {
                    floor -= 1;
                    // Count the number of persons queued to go below the
                    // current floor.
                    let mut count_down = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if (*item as usize) < floor {
                            count_down += 1;
                        }
                    }
                    // Count the number of riders wanting to get off
                    // at the current floor
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_down + count_off > 0 {
                        return Some(floor as u32);
                    }
                }
                None
            }
            Direction::Down => {
                // work from the bottom floor up
                floor = 0;
                while floor < self.queues.len()  {
                    
                    // Count the number of persons queued to go above the
                    // current floor.
                    let mut count_up = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if (*item as usize) > floor {
                            count_up += 1;
                        }
                    }
                    // Count the number of riders wanting to get off
                    // at the current floor
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_up + count_off > 0 {
                        return Some(floor as u32);
                    }

                    floor += 1;
                }
                None
            }
        }
    }
    
    /// This function stop_at_floor carries out needed actions while stopped at the current floor.
    /// Assumption: we should have guaranteed this floor is the next needed stop.
    /// The needed direction should alread have been set.
    fn stop_at_floor(&mut self, floor: u32) -> () {
        // Set the LiftState to the designated floor.
        self.floor = floor;
        // println!("Starting stop_at_floor: {}  {:?}", floor, self.direction);
        // Let off riders for the designated floor.
        let mut new_riders: Vec<u32> = vec![];
        for rider in &self.riders {
            if *rider != floor {
                // riders not for this floor remain on the lift
                new_riders.push(*rider);
            }
        }
        // Let queued passengers onto the lift up to the lift capacity.
        let mut new_queued: Vec<u32> = vec![];
        for queued in &self.queues[floor as usize] {
            // Only admit riders who want to go in current direction of the lift.
            let admit: bool;
            match self.direction {
                Direction::Up => {
                    admit = *queued > floor;
                }
                Direction::Down => {
                    admit = *queued < floor;
                }
            }
            // And only allow new riders to enter up to the lift capacity.
            // Persons not admitted remain in the revised queue.
            if admit && new_riders.len() < (self.capacity as usize) {
                // Admit one rider
                new_riders.push(*queued);
            } else {
                // Otherwise rider remains in queue for this floor...
                new_queued.push(*queued);
            }
        }
        // Now update both the queue and lift riders for this floor:
        self.riders.clear();
        self.riders.extend(new_riders);
        self.queues[floor as usize].clear();
        self.queues[floor as usize].extend(new_queued);
        // If an extreme up or down floor has been reached, the Lift must reverse direction:
        if self.floor == 0 {
            self.direction = Direction::Up;
        }
        if self.floor as usize == self.queues.len() - 1 {
            self.direction = Direction::Down;
        }
        // println!("end stop_at_floor printing queues...");
        // print_queues(&self.queues, self.capacity, &self.riders);
    }

    /// This function finds the closest floor to pick up or drop off
    /// passengers while continuing to travel in the current direction.
    fn find_next_stop_forward(&self) -> Option<u32> {
        // println!("starting find_next_stop_forward() direction = {:?} starting floor {}", self.direction, self.floor);
        let mut floor = self.floor as usize;
        match self.direction {   
            Direction::Up => {
                // println!("up printing queues...");
                // print_queues(&self.queues, self.capacity, &self.riders);
                while floor < self.queues.len() - 2 {
                    floor += 1;
                    // Count the number of persons queued to go above the
                    // current floor.
                    let mut count_up = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if *item as usize > floor {
                            count_up += 1;
                        }
                    }
                    // Count the number of riders wanting to get off
                    // at the current floor
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_up + count_off > 0 {
                        return Some(floor as u32);
                    }
                }
                None
            }
            Direction::Down => {
                while floor > 0 {
                    floor -= 1;
                    // Count the number of persons queued to go below the
                    // current floor.
                    let mut count_down = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if (*item as usize) < floor {
                            count_down += 1;
                        }
                    }
                    // Count the number of riders wanting to get off
                    // at the current floor
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_down + count_off > 0 {
                        return Some(floor as u32);
                    }
                }
                None
            }
        }
    }
}


fn print_queues(queues: &Vec<Vec<u32>>, capacity: u32, riders: &Vec<u32>) -> String {
    let mut result = format!("\nLift capacity = {capacity}\n\n Floor    Queue");
    for (i, q) in queues.iter().enumerate().rev() {
        result.push_str(&format!("\n{i:>4} .... {q:?}"));
    }
    result.push_str(&format!("\n riders: {:?}", riders));
    println!("{}", result);
    result
}


// Add your tests here.
// See https://doc.rust-lang.org/stable/rust-by-example/testing/unit_testing.html

#[cfg(test)]
mod tests {
    use super::the_lift;
    
    fn print_queues(queues: &[Vec<u32>], capacity: u32) -> String {
        let mut result = format!("\nLift capacity = {capacity}\n\n Floor    Queue");
        for (i, q) in queues.iter().enumerate().rev() {
            result.push_str(&format!("\n{i:>4} .... {q:?}"));
        }
        result
    }

    fn do_test(queues: &[Vec<u32>], capacity: u32, expected: &[u32]) {
        let actual = the_lift(queues, capacity);
        assert_eq!(actual, expected,
            "\nYour result (left) did not match expected output (right) for the given queues:\n{}\n",
            print_queues(queues, capacity));
    }

    #[test]
    fn test_up() {
        do_test(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5, &[0, 2, 5, 0]);
    }
    #[test]
    fn test_down() {
        do_test(&[vec![],vec![],vec![1],vec![],vec![],vec![],vec![]], 5, &[0, 2, 1, 0]);
    }
    #[test]
    fn test_up_and_up() {
        do_test(&[vec![],vec![3],vec![4],vec![],vec![5],vec![],vec![]], 5, &[0, 1, 2, 3, 4, 5, 0]);
    }
    #[test]
    fn test_down_and_down() {
        do_test(&[vec![],vec![0],vec![],vec![],vec![2],vec![3],vec![]], 5, &[0, 5, 4, 3, 2, 1, 0]);
    }
    #[test]
    fn test_loaded_floors() {
        do_test(&[vec![],vec![0,0,0,0],vec![0,0,0,0],vec![0,0,0,0],vec![0,0,0,0],vec![0,0,0,0],vec![0,0,0,0]], 5, 
            &[0, 6, 5, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 4, 3, 2, 1, 0, 3, 2, 1, 0, 1, 0]);
    }
    #[test]
    fn test_loaded_eleven() {
        do_test(&[vec![],vec![],vec![],vec![1,1,1,1,1,1,1,1,1,1,1],vec![],vec![],vec![]], 5, &[0, 3, 1, 3, 1, 3, 1, 0]);
    }
}
